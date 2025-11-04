import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name="ddxzzsw5h",
    api_key="419481224295258",
    api_secret="08F1j3V0Wc_CZnl_frE9GcAe0yI"
)

result = cloudinary.uploader.upload("bgggg.jpg")
print(result)  # Bu yerda full response: url, public_id, format, size...
