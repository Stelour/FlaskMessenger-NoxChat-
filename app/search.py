from flask import current_app
from elasticsearch import NotFoundError

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
    try:
        current_app.elasticsearch.delete(index=index, id=model.id)
    except NotFoundError:
        return
    except Exception:
        current_app.logger.exception('Elasticsearch delete failed; skipping')

def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    try:
        es_query = {
            'multi_match': {
                'query': query,
                'fields': ['username^2', 'public_id']
            }
        }
        search = current_app.elasticsearch.search(
            index=index,
            query=es_query,
            from_=(page - 1) * per_page,
            size=per_page,
        )
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        total_obj = search['hits'].get('total', {})
        total = total_obj.get('value', 0) if isinstance(total_obj, dict) else total_obj
        return ids, total
    except Exception:
        current_app.logger.exception('Elasticsearch query failed; falling back to DB')
        raise