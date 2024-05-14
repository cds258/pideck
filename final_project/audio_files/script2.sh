for file in *.mov; do
    ffmpeg -i "$file" -acodec pcm_s16le -ar 44100 -ac 2 "${file%.mov}.wav"
done