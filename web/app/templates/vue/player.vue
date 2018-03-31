<template id="player">
  <div class="card">
    <div class="player-header">
      <button @click="video.close_video(video)" type="button" class="player-close" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>

    </div>
    <div class="card-body player-body">
      <div class="poo">
        <div class="video">
          <iframe v-if="video.video_type === 'youtube'"
              title="Video player" class="youtube-player" type="text/html"

                  :src="video.url"
                  :height="this.height"
                  :width="this.width"
                  frameborder="0" allowFullScreen style="display: block; margin: auto;">
          </iframe>
          <iframe v-else
              title="Video player" class="youtube-player" type="text/html"
                  :src="'https://ipfs.io/ipfs/' + video.video_id"
                  :height="this.height"
                  :width="this.width"
                  frameborder="0" allowFullScreen style="display: block; margin: auto;">
          </iframe>
        </div>
        <p>{{ video.title }}</p>
      </div>
    </div>

  </div>
  </div>
</template>