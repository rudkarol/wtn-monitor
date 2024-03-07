import httpx
from discord import Webhook, Embed, colour
from datetime import datetime

import settings


def build_embed(offer: dict[str, str], title: str, color: colour) -> Embed:
    embed = Embed(title=title, color=color, timestamp=datetime.utcnow())

    embed.add_field(name='ID', value=offer['id'], inline=False)
    embed.add_field(name='Price', value=str(offer['price']), inline=False)
    embed.add_field(name='Size', value=offer['europeanSize'], inline=False)
    embed.add_field(name='Listing price', value=str(offer['listingPrice']), inline=False)
    embed.add_field(name='Variant', value=str(offer['variantId']), inline=False)
    embed.set_footer(text='WTN Offer Sniper | github@xlorek')
    embed.set_thumbnail(url=offer['image'])

    return embed


async def accepted_webhook(offer: dict[str, str]):
    title = 'Offer accepted! - ' + offer['name']
    embed = build_embed(offer=offer, title=title, color=0x00c703)

    await send_webhook(embed=embed)


async def offer_webhook(offer: dict[str, str]):
    title = 'New offer - ' + offer['name']
    embed = build_embed(offer=offer, title=title, color=0xbfbfbf)

    await send_webhook(embed=embed)


async def send_webhook(embed: Embed):
    async with httpx.AsyncClient() as client:
        webhook = Webhook.from_url(url=settings.WEBHOOK_URL, session=client)
        await webhook.send(embed=embed)
