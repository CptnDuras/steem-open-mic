<template id="searchresultspage">
  <div class='searchresultspage'>

    <b-container class="video-horizontal-panel">
      <h4 v-if="videos.length>0" style="padding-left:10px">Search Results matching '{{ $route.params.search_terms }}'<span style="color:red;font-size: 0.7em;" v-if="$globals.filter_not_default"> (filtered)</span></h4>
      <h4 v-else style="padding-left:10px">Sorry, No Search Results matching '{{ $route.params.search_terms }}'<span style="color:red;font-size: 0.7em;" v-if="$globals.filter_not_default"> (filtered)</span></h4>
      <b-row>

        <b-col sm="12" md="6" lg="4" xl="3" v-for="v in videos" :key="v.author + v.permlink">
            <div style="padding-bottom:15px">
                <div style="position:relative;padding:5px">
                    <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
                    <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                        <b-img-lazy @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)" v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center fluid :src="v.video_thumbnail_image_url" class="thumbnail-image"/> 
                    </div>
                </div>
                <div class="video-info-panel">
                  <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)" v-text="v.title_truncated"></div>
                  <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author }}</a> - 
                    <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                    <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                    <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span> 
                    on 
                    <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dtube-icon.png'/>
                    </a>
                    <a v-if="v.video_type=='dlive'" :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                      <b-img src='/dist/images/dlive-icon.png'/>
                    </a>
                    <a v-if="v.video_type=='youtube'" :href="'https://www.youtube.com/watch?v=' + v.video_id" target="_blank">
                      <b-img src='/dist/images/youtube-icon.png'/>
                    </a>
                  </div>
                  <div class="video-payout-string">{{ v.payout_string }}</div>
                </div>
            </div>
        </b-col>

        <infinite-loading ref="infiniteLoading" @infinite="infiniteHandler">
          <span slot="no-results"></span>
        </infinite-loading>

      </b-row>
    </b-container>

  </div>
</template>