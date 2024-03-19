import asyncio
from discord import Webhook, Embed, colour
from datetime import datetime
from aiohttp import ClientSession


def build_embed(offer: dict[str, str], title: str, color: colour) -> Embed:
    embed = Embed(title=title, color=color, timestamp=datetime.strptime(offer['createTime'], "%Y-%m-%dT%H:%M:%S.%fZ"))

    embed.add_field(name='SKU', value=offer['sku'], inline=False)
    embed.add_field(name='Price', value=str(offer['price']), inline=False)
    embed.add_field(name='Size', value=offer['europeanSize'], inline=False)
    embed.add_field(name='Listing price', value=str(offer['listingPrice']), inline=False)
    embed.add_field(name='Variant', value=str(offer['variantId']), inline=False)
    embed.add_field(name='Offer ID', value=offer['id'], inline=False)
    embed.set_footer(text='WTN Offer Sniper | github@xlorek')
    embed.set_thumbnail(url=offer['image'])

    return embed


def accepted_webhook(data: dict[str, str], url: str, additional_mess: str = ''):
    embed = build_embed(
        offer=data,
        title='Offer accepted! - ' + data['name'] + additional_mess,
        color=0x00c703
    )

    asyncio.run(send_webhook(embed, url))


def offer_webhook(data: dict[str, str], url: str):
    embed = build_embed(
        offer=data,
        title='New offer - ' + data['name'],
        color=0xbfbfbf
    )

    asyncio.run(send_webhook(embed, url))


def failed_webhook(data: dict[str, str], url: str):
    embed = build_embed(
        offer=data,
        title='Failed to accept offer - ' + data['name'],
        color=0xff2b2b
    )

    asyncio.run(send_webhook(embed, url))


def error_webhook(mess: str, url: str):
    embed = Embed(title=mess, color=0xff2b2b, timestamp=datetime.utcnow())

    asyncio.run(send_webhook(embed, url))


async def send_webhook(embed: Embed, url: str):
    try:
        async with ClientSession() as client:
            webhook = Webhook.from_url(url=url, session=client)
            await webhook.send(embed=embed)
    except Exception:
        pass
