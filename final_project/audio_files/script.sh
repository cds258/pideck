for file in *.mp3; do
    ffmpeg -i "$file" -acodec pcm_s16le -ar 44100 -ac 2 "${file%.mp3}.wav"
done
