a = {"a": "a", "b": "b"}


print(
    list(
        map(
            lambda x: tuple(
                map(lambda y: y.encode(), x)), a.items()
        )
    )
)