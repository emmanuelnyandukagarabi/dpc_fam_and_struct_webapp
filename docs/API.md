# DPC Webapp API

The API exposes read-only JSON endpoints for DPCFam metaclusters,
DPCStruct metaclusters, and Pfam domain matches.

Run the local development server:

```bash
.venv/bin/python manage.py runserver 0.0.0.0:8001
```

Use this base URL locally:

```text
http://127.0.0.1:8001/api/
```

## Pagination

List responses are paginated. Use:

```text
page=1
page_size=25
```

`page_size` is capped at `100`.

Example paginated response shape:

```json
{
  "count": 28246,
  "page": 1,
  "page_size": 25,
  "total_pages": 1130,
  "has_next": true,
  "has_previous": false,
  "results": []
}
```

## Endpoints

### List DPCFam Metaclusters

```http
GET /api/dpcfam/metaclusters/
```

Examples:

```bash
curl "http://127.0.0.1:8001/api/dpcfam/metaclusters/?page=1&page_size=10"
curl "http://127.0.0.1:8001/api/dpcfam/metaclusters/?dataset=standard&page_size=10"
curl "http://127.0.0.1:8001/api/dpcfam/metaclusters/?dataset=b&page_size=10"
```

Optional query parameters:

```text
dataset=standard
dataset=b
page=1
page_size=25
```

### Retrieve One DPCFam Metacluster

```http
GET /api/dpcfam/metaclusters/<mcid>/
```

Example:

```bash
curl "http://127.0.0.1:8001/api/dpcfam/metaclusters/MC1/?page_size=5"
```

The response contains:

```text
metacluster
sequences
alphafolds
```

### List DPCStruct Metaclusters

```http
GET /api/dpcstruct/metaclusters/
```

Examples:

```bash
curl "http://127.0.0.1:8001/api/dpcstruct/metaclusters/?page=1&page_size=10"
curl "http://127.0.0.1:8001/api/dpcstruct/metaclusters/?search_mcid=MC10&page_size=10"
```

Optional query parameters:

```text
search_mcid=MC10
page=1
page_size=25
```

### Retrieve One DPCStruct Metacluster

```http
GET /api/dpcstruct/metaclusters/<mcid>/
```

Example:

```bash
curl "http://127.0.0.1:8001/api/dpcstruct/metaclusters/MC0/?page_size=5"
```

The response contains:

```text
metacluster
sequences
cath_annotations
scop_annotations
```

### Retrieve Pfam Matches

```http
GET /api/pfam/<pfam_id>/
```

Example:

```bash
curl "http://127.0.0.1:8001/api/pfam/CL0186/?page_size=10"
```

The response contains the Pfam domain and matching metaclusters from both
DPCFam and DPCStruct:

```text
pfam
dpcfam_metaclusters
dpcstruct_metaclusters
```

## Browser Usage

You can also paste any API URL directly into a browser. For example:

```text
http://127.0.0.1:8001/api/dpcstruct/metaclusters/?page_size=3
http://127.0.0.1:8001/api/dpcstruct/metaclusters/MC0/?page_size=3
http://127.0.0.1:8001/api/pfam/CL0186/?page_size=3
```
