<template id="home">
  <div class='homepage'>
    <transition name="fade">
      <player v-if="player_show" :video="current_video"></player>
    </transition>
    <div class="video-horizontal-panel">
      <h4 style="padding-left:10px">
        Hot Videos
      </h4>
      <div class="carousel-container">
        <div class="carousel">
          {## this gets populated by JS ##}
          <component v-for='video in hot_videos'
                     :key="video.video_id"
                     :is='video.mode'
                     :video='video'
          >
          </component>
        </div>
      </div>
    </div>

  </div>
</template>
