FROM curlimages/curl:8.9.1
CMD ["sh", "-lc", "curl -sS -X POST \"$API_URL\" -H 'Content-Length: 0' || exit 1"]

