from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

SEARCH_HISTORY_RESPONSE = {
    "stats": [
        {"city__name": "Moscow", "count": 5},
        {"city__name": "London", "count": 3}
    ]
}

search_history_docs = extend_schema(
    summary="История поиска",
    description="Возвращает статистику поиска городов пользователем",
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Успешный ответ",
            examples=[
                OpenApiExample(
                    "Пример успешного ответа",
                    value=SEARCH_HISTORY_RESPONSE
                )
            ]
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Ошибка авторизации",
            examples=[
                OpenApiExample(
                    "Пример ошибки",
                    value={"detail": "Неверные логин или пароль."}
                )
            ]
        )
    },
)

search_history_dict = {
    "summary": "История поиска",
    "description": "Возвращает статистику поиска городов пользователем",
    "responses": {
        200: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Успешный ответ",
            examples=[
                OpenApiExample(
                    "Пример успешного ответа",
                    value=SEARCH_HISTORY_RESPONSE
                )
            ]
        ),
        401: OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            description="Ошибка авторизации",
            examples=[
                OpenApiExample(
                    "Пример ошибки",
                    value={"detail": "Неверные логин или пароль."}
                )
            ]
        )
    },
    # "auth": [{'basic': []}],
    "tags": ["История"]
}
