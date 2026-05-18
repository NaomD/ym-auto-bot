"""
Crypto Alert & Tracker Telegram Bot
Professional Cryptocurrency Price Tracking Solution
"""

import telebot
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot with token from BotFather
# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '8662703857:AAGY04D4oqsDe5nnz1bCBefh6q3E9gfz1Fs'
bot = telebot.TeleBot(BOT_TOKEN)

# CoinGecko API base URL
COINGECKO_API_URL = 'https://api.coingecko.com/api/v3'

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Handle /start command - Send professional welcome message
    """
    try:
        welcome_text = (
            "👋 Welcome to *Crypto Alert & Tracker Bot*!\n\n"
            "📈 Professional cryptocurrency tracking solution at your fingertips.\n\n"
            "*Available Commands:*\n"
            "/price `<coin>` - Get real-time price of any cryptocurrency\n"
            "/trending - View top 5 trending cryptocurrencies\n"
            "/start - Show this help message\n\n"
            "_Powered by CoinGecko API_"
        )
        bot.reply_to(message, welcome_text, parse_mode='Markdown')
        logger.info(f"User {message.from_user.username} started the bot")
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")
        bot.reply_to(message, "❌ An error occurred. Please try again later.")

@bot.message_handler(commands=['price'])
def get_crypto_price(message):
    """
    Handle /price command - Get cryptocurrency price from CoinGecko
    Usage: /price bitcoin or /price btc
    """
    try:
        # Extract coin name from message
        coin_name = message.text.split(' ', 1)[1].lower() if len(message.text.split(' ')) > 1 else None
        
        if not coin_name:
            bot.reply_to(message, "❗ Please specify a cryptocurrency.\nExample: `/price bitcoin`", parse_mode='Markdown')
            return
            
        # Fetch coin data from CoinGecko
        response = requests.get(
            f"{COINGECKO_API_URL}/coins/markets",
            params={
                'vs_currency': 'usd',
                'ids': coin_name,
                'order': 'market_cap_desc',
                'per_page': 1,
                'page': 1,
                'sparkline': False
            },
            timeout=10
        )
        
        if response.status_code != 200:
            bot.reply_to(message, "❌ Unable to fetch data. Please check the coin name and try again.")
            return
            
        data = response.json()
        
        if not data:
            bot.reply_to(message, f"❓ Sorry, '{coin_name}' not found. Please check the coin name and try again.")
            return
            
        coin = data[0]
        price = coin['current_price']
        price_change_24h = coin['price_change_percentage_24h']
        market_cap = coin['market_cap']
        volume = coin['total_volume']
        
        # Format response message
        emoji = "🟢" if price_change_24h >= 0 else "🔴"
        price_message = (
            f"*{coin['name']} ({coin['symbol'].upper()})*\n"
            f"{emoji} Price: ${price:,}\n"
            f"{'⬆️' if price_change_24h >= 0 else '⬇️'} 24h Change: {price_change_24h:.2f}%\n"
            f"💰 Market Cap: ${market_cap:,}\n"
            f"📊 Volume (24h): ${volume:,}\n"
            f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        
        bot.reply_to(message, price_message, parse_mode='Markdown')
        logger.info(f"Price requested for {coin_name}")
        
    except IndexError:
        bot.reply_to(message, "❗ Please specify a cryptocurrency.\nExample: `/price bitcoin`", parse_mode='Markdown')
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in get_crypto_price: {e}")
        bot.reply_to(message, "🌐 Network error. Please try again later.")
    except Exception as e:
        logger.error(f"Error in get_crypto_price: {e}")
        bot.reply_to(message, "❌ An unexpected error occurred. Please try again later.")

@bot.message_handler(commands=['trending'])
def get_trending_coins(message):
    """
    Handle /trending command - Get top 5 trending cryptocurrencies from CoinGecko
    """
    try:
        # Fetch trending coins from CoinGecko
        response = requests.get(
            f"{COINGECKO_API_URL}/search/trending",
            timeout=10
        )
        
        if response.status_code != 200:
            bot.reply_to(message, "❌ Unable to fetch trending data. Please try again later.")
            return
            
        data = response.json()
        coins = data.get('coins', [])[:5]  # Limit to top 5
        
        if not coins:
            bot.reply_to(message, "📉 No trending coins data available at the moment.")
            return
            
        # Format trending coins message
        trending_message = "*🔥 Top 5 Trending Cryptocurrencies*\n\n"
        for i, coin in enumerate(coins, 1):
            coin_data = coin.get('item', {})
            name = coin_data.get('name', 'N/A')
            symbol = coin_data.get('symbol', 'N/A').upper()
            price_btc = coin_data.get('price_btc', 'N/A')
            
            trending_message += f"{i}. *{name}* ({symbol})\n"
            trending_message += f"   💰 Price: ฿{price_btc}\n\n"
            
        trending_message += f"⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        bot.reply_to(message, trending_message, parse_mode='Markdown')
        logger.info("Trending coins requested")
        
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error in get_trending_coins: {e}")
        bot.reply_to(message, "🌐 Network error. Please try again later.")
    except Exception as e:
        logger.error(f"Error in get_trending_coins: {e}")
        bot.reply_to(message, "❌ An unexpected error occurred. Please try again later.")

# Start polling for messages
if __name__ == "__main__":
    logger.info("Crypto Alert & Tracker Bot is starting...")
    bot.infinity_polling()
