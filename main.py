import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import re

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Replace with your actual bot token
TOKEN = "7558561191:AAE4KBjYYpL3lgGAccRI-TY9OLesCQFRdbM"

# Supported platforms and their URL patterns
URL_PATTERNS = {
    "youtube": r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
    "instagram": r"(https?://)?(www\.)?(instagram\.com)/",
    "tiktok": r"(https?://)?(www\.)?(tiktok\.com)/",
    "twitter": r"(https?://)?(www\.)?(twitter\.com|x\.com)/",
    "facebook": r"(https?://)?(www\.)?(facebook\.com|fb\.watch)/",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "👋 Salom! Men video yuklovchi botman. Menga YouTube, Instagram, TikTok, Twitter yoki Facebook havolasini yuboring, men sizga videoni yuklab beraman."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Botdan foydalanish uchun quyidagi platformalardan birining havolasini yuboring:\n"
        "- YouTube\n"
        "- Instagram\n"
        "- TikTok\n"
        "- Twitter\n"
        "- Facebook\n\n"
        "Men sizga videoni yuklab beraman."
    )

def is_valid_url(text: str) -> bool:
    """Check if the message contains a valid URL from supported platforms."""
    for platform, pattern in URL_PATTERNS.items():
        if re.search(pattern, text):
            return True
    return False

def get_platform(url: str) -> str:
    """Determine which platform the URL is from."""
    for platform, pattern in URL_PATTERNS.items():
        if re.search(pattern, url):
            return platform
    return "unknown"

async def download_video(url: str) -> str:
    """Download video from URL using yt-dlp."""
    output_template = "downloads/%(title)s.%(ext)s"
    
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user message."""
    message_text = update.message.text
    
    # Check if the message contains a URL
    if is_valid_url(message_text):
        platform = get_platform(message_text)
        status_message = await update.message.reply_text(
            f"🔄 {platform.capitalize()} havolasi aniqlandi. Video yuklanmoqda..."
        )
        
        try:
            # Download the video
            await update.message.reply_text("⏳ Video yuklanmoqda, iltimos kuting...")
            video_path = await download_video(message_text)
            
            # Send the video
            await update.message.reply_text("📤 Video yuborilmoqda...")
            with open(video_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=f"✅ {platform.capitalize()}dan yuklangan video",
                    supports_streaming=True
                )
            
            # Delete the downloaded file to save space
            os.remove(video_path)
            await status_message.delete()
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Xatolik yuz berdi: {str(e)}\n"
                "Iltimos, boshqa havola bilan urinib ko'ring yoki /help buyrug'ini yuboring."
            )
    else:
        await update.message.reply_text(
            "🔍 Havola aniqlanmadi. Iltimos, qo'llab-quvvatlanadigan platformadan video havolasini yuboring."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    print("Bot started!")
    main()