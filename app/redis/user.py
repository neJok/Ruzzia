from redis.asyncio import Redis


async def right_add_to_queue(
    r: Redis,
    address: str
) -> None:
    await r.rpush("registration_queue", address)


async def left_get_position_in_queue(
    r: Redis,
    value: str
) -> int | None:
    return await r.lpos("registration_queue", value)


async def left_remove_from_queue(r: Redis) -> None:
    await r.lpop("registration_queue")
