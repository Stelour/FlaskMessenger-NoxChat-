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
    try:
        current_app.elasticsearch.delete(index=index, id=model.id)
    except Exception:
        # ignore missing docs or transient delete issues during development
        current_app.logger.debug('Elasticsearch delete skipped or failed silently')


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    try:
        search = current_app.elasticsearch.search(
            index=index,
            query={'multi_match': {'query': query, 'fields': ['*']}},
            from_=(page - 1) * per_page,
            size=per_page,
        )
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        total = search['hits']['total']['value'] if 'hits' in search and 'total' in search['hits'] else 0
        return ids, total
    except Exception:
        current_app.logger.exception('Elasticsearch query failed; returning empty')
        return [], 0
