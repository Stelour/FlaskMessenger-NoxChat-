from flask import current_app

def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {field: getattr(model, field) for field in model.__searchable__}
    try:
        current_app.elasticsearch.index(index=index, id=model.id, document=payload)
    except Exception:
        current_app.logger.exception('Elasticsearch indexing failed; skipping')

def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    try:
        search = current_app.elasticsearch.search(...);
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']['value']
    except Exception:
        current_app.logger.exception('Elasticsearch query failed; returning empty')
        return [], 0