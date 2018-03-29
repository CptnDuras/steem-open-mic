<template id="video_tile">
  <div>
    <a @click="video.play_video(video)" :title="video.title">
        <img :data-lazy="video.img" :alt="video.title" class="img-responsive" height="130px" />
        <h4>{{ video.title_truncated }}...</h4>
        <span class="glyphicon glyphicon-play-circle"></span>
        <span class="upload">{{ video.upload_time }}</span>
    </a>
  </div>
</template>