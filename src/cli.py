
from __future__ import annotations
import asyncio, json, os, yaml
from typing import List
import typer, pandas as pd
from src.pipelines.write_jsonl import JsonlWriter
from src.sites.indiamart import IndiaMartFetcher
from src.sites.alibaba import AlibabaFetcher
app = typer.Typer(add_completion=False, no_args_is_help=True)
def load_yaml(path:str):
    with open(path,"r",encoding="utf-8") as f: return yaml.safe_load(f)
@app.command()
def crawl(site: str = typer.Option("both", help="indiamart|alibaba|both"),
          categories_cfg: str = typer.Option("configs/categories.yaml"),
          settings_cfg: str = typer.Option("configs/settings.yaml"),
          out: str = typer.Option("data/raw/products.jsonl"),
          max_pages: int = typer.Option(2)):
    cfg=load_yaml(categories_cfg); st=load_yaml(settings_cfg)
    user_agents: List[str]=st.get("user_agent_pool", []); proxy=st.get("proxy") or None; respect_robots=bool(st.get("respect_robots", True))
    base_delay=float(st.get("base_delay_seconds",1.2)); jitter=float(st.get("jitter_seconds",1.0))
    ind=IndiaMartFetcher(user_agents, proxy=proxy, respect_robots=respect_robots)
    ali=AlibabaFetcher(user_agents, proxy=proxy, respect_robots=respect_robots)
    jw=JsonlWriter(out)
    async def do_ind(cat):
        for q in cat.get("indiamart", {}).get("search_queries", []):
            async for item in ind.iter_search(q, max_pages=max_pages, base_delay=base_delay, jitter=jitter):
                jw.write_one(item.model_dump())
        urls=cat.get("indiamart", {}).get("category_urls", [])
        async for item in ind.iter_category_pages(urls, label=cat["slug"], base_delay=base_delay, jitter=jitter):
            jw.write_one(item.model_dump())
    async def do_ali(cat):
        urls=cat.get("alibaba", {}).get("showroom_urls", [])
        async for item in ali.iter_showrooms(urls, label=cat["slug"], base_delay=base_delay, jitter=jitter):
            jw.write_one(item.model_dump())
    async def main():
        for cat in cfg.get("categories", []):
            if site in ("indiamart","both"): await do_ind(cat)
            if site in ("alibaba","both"): await do_ali(cat)
    asyncio.run(main()); jw.close(); typer.echo(f"Saved: {out}")
@app.command()
def clean(inp: str = typer.Option("data/raw/products.jsonl"),
          out: str = typer.Option("data/clean/products.csv")):
    rows=[]; 
    with open(inp,"rb") as f:
        for line in f:
            if not line.strip(): continue
            rows.append(json.loads(line))
    if not rows: typer.echo("No input rows."); raise typer.Exit(1)
    df=pd.DataFrame(rows)
    if "product_page_url" in df: df=df.drop_duplicates(subset=["product_page_url"], keep="first")
    else: df=df.drop_duplicates(subset=["title","site"], keep="first")
    os.makedirs(os.path.dirname(out), exist_ok=True); df.to_csv(out, index=False); typer.echo(f"Wrote {out} ({len(df)} rows)")
@app.command()
def eda(inp: str = typer.Option("data/clean/products.csv")):
    from src.eda.eda_report import run as run_eda; run_eda(inp)
if __name__=="__main__": app()
