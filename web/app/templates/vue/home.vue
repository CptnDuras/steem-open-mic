<template id="home">
  <div class='homepage'>

    <b-container class="video-horizontal-panel">
      <h4 style="padding-left:10px">
        <router-link :to="{ path: '/hot' }">Hot Videos</router-link>
      </h4>
      <carousel :minSwipeDistance="100" :perPage="1"
                :perPageCustom="[[601, 2], [801, 3], [1101, 4], [1351, 5], [1600, 6]]" navigationEnabled
                navigationPrevLabel="<img src='/dist/images/left-arrow.png'/>"
                scrollPerPage @touchend.native="loadNewlyDisplayedImages" @mouseup.native="loadNewlyDisplayedImages">

        <!-- todo - improve lazy loading, currently in slide //-->
        <slide v-for="v in hot_videos" :key="v.author + v.permlink">
          <div>
            <div style="position:relative;padding:5px;margin-right:0px">
              <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
              <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                <b-img-lazy offset="1000" class="thumbnail-image"
                            @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)"
                            v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center
                            fluid :src="v.video_thumbnail_image_url"/>
              </div>
            </div>
            <div class="video-info-panel">
              <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)">{{
                v.title_truncated }}
              </div>
              <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author
                }}</a> -
                <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span>
                on
                <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink"
                   target="_blank">
                  <b-img src='/dist/images/dtube-icon.png'/>
                </a>
                <span v-if="v.video_type=='dlive'">
                      <a v-if="v.video_id=='live'"
                         :href="'https://www.dlive.io/#/livestream/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img style="background:#AAFFAA" src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-else :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>                      
                    </span>
                <a v-if="v.video_type=='youtube'" :href="'https://www.youtube.com/watch?v=' + v.video_id"
                   target="_blank">
                  <b-img src='/dist/images/youtube-icon.png'/>
                </a>
              </div>
              <div style="text-align:center">
                <span class="video-payout-string">{{ v.payout_string }}</span>
                <trend v-if="v.votes_sparkline_data"
                       :width="30"
                       :height="12"
                       :data="JSON.parse(v.votes_sparkline_data)"
                       :gradient="['#000', '#000', '#000']"
                       :stroke-width="1"
                       :padding="1"
                >
                </trend>
              </div>
            </div>
          </div>
        </slide>
      </carousel>
    </b-container>

    <hr>

    <b-container class="video-horizontal-panel">
      <h4 style="padding-left:10px">
        <router-link :to="{ path: '/trending' }">Trending Videos</router-link>
      </h4>
      <carousel :minSwipeDistance="100" :perPage="1"
                :perPageCustom="[[601, 2], [801, 3], [1101, 4], [1351, 5], [1600, 6]]" navigationEnabled
                navigationNextLabel="<img src='/dist/images/right-arrow.png'/>"
                navigationPrevLabel="<img src='/dist/images/left-arrow.png'/>"
                scrollPerPage @touchend.native="loadNewlyDisplayedImages" @mouseup.native="loadNewlyDisplayedImages">

        <!-- todo - improve lazy loading, currently in slide //-->
        <slide v-for="v in trending_videos" :key="v.author + v.permlink">
          <div>
            <div style="position:relative;padding:5px;margin-right:0px">
              <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
              <div class="som-thumbnail">
                <b-img-lazy offset="1000" class="thumbnail-image"
                            @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)"
                            v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center
                            fluid :src="v.video_thumbnail_image_url"/>
              </div>
            </div>
            <div class="video-info-panel">
              <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)">{{
                v.title_truncated }}
              </div>
              <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author
                }}</a> -
                <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span>
                on
                <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink"
                   target="_blank">
                  <b-img src='/dist/images/dtube-icon.png'/>
                </a>
                <span v-if="v.video_type=='dlive'">
                      <a v-if="v.video_id=='live'"
                         :href="'https://www.dlive.io/#/livestream/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img style="background:#AAFFAA" src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-else :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>                      
                    </span>
                <a v-if="v.video_type=='youtube'" :href="'https://www.youtube.com/watch?v=' + v.video_id"
                   target="_blank">
                  <b-img src='/dist/images/youtube-icon.png'/>
                </a>
              </div>
              <div style="text-align:center">
                <span class="video-payout-string">{{ v.payout_string }}</span>
                <trend v-if="v.votes_sparkline_data"
                       :width="30"
                       :height="12"
                       :data="JSON.parse(v.votes_sparkline_data)"
                       :gradient="['#000', '#000', '#000']"
                       :stroke-width="1"
                       :padding="1"
                >
                </trend>
              </div>
            </div>
          </div>
        </slide>
      </carousel>
    </b-container>

    <hr>

    <b-container class="video-horizontal-panel">
      <h4 style="padding-left:10px">
        <router-link :to="{ path: '/new' }">New Videos</router-link>
      </h4>
      <carousel :minSwipeDistance="100" :perPage="1"
                :perPageCustom="[[601, 2], [801, 3], [1101, 4], [1351, 5], [1600, 6]]" navigationEnabled
                navigationNextLabel="<img src='/dist/images/right-arrow.png'/>"
                navigationPrevLabel="<img src='/dist/images/left-arrow.png'/>"
                scrollPerPage @touchend.native="loadNewlyDisplayedImages" @mouseup.native="loadNewlyDisplayedImages">

        <!-- todo - improve lazy loading, currently in slide //-->
        <slide v-for="v in new_videos" :key="v.author + v.permlink">
          <div>
            <div style="position:relative;padding:5px">
              <span class="duration-label">&nbsp;{{ v.duration_string }}&nbsp;</span>
              <div style="cursor:pointer;z-index:998;background-color:rgb(0,0,0);">
                <b-img-lazy offset="1000" class="thumbnail-image"
                            @contextmenu.native.prevent="playVideo(v.author, v.permlink, v.video_type, v.video_id, true)"
                            v-on:click.native="playVideo(v.author, v.permlink, v.video_type, v.video_id, false)" center
                            fluid :src="v.video_thumbnail_image_url"/>
              </div>
            </div>
            <div class="video-info-panel">
              <div class="video-title" v-on:click="playVideo(v.author, v.permlink, v.video_type, v.video_id)">{{
                v.title_truncated }}
              </div>
              <div class="video-author-age"><a target="_blank" :href="'https://steemit.com/@' + v.author ">{{ v.author
                }}</a> -
                <span v-if="v.video_post_delay_days==0"><font color="#66BB66">{{ v.age_string }}</font></span>
                <span v-else-if="v.video_post_delay_days<=7">{{ v.age_string }}</span>
                <span v-else=""><font color="#BB6666">{{ v.age_string }}</font></span>
                on
                <a v-if="v.video_type=='dtube'" :href="'https://d.tube/#!/v/' + v.author + '/' + v.permlink"
                   target="_blank">
                  <b-img src='/dist/images/dtube-icon.png'/>
                </a>
                <span v-if="v.video_type=='dlive'">
                      <a v-if="v.video_id=='live'"
                         :href="'https://www.dlive.io/#/livestream/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img style="background:#AAFFAA" src='/dist/images/dlive-icon.png'/>
                      </a>
                      <a v-else :href="'https://www.dlive.io/#/video/' + v.author + '/' + v.permlink" target="_blank">
                        <b-img src='/dist/images/dlive-icon.png'/>
                      </a>                      
                    </span>
                <a v-if="v.video_type=='youtube'" :href="'https://www.youtube.com/watch?v=' + v.video_id"
                   target="_blank">
                  <b-img src='/dist/images/youtube-icon.png'/>
                </a>
              </div>
              <div style="text-align:center">
                <span class="video-payout-string">{{ v.payout_string }}</span>
                <trend v-if="v.votes_sparkline_data"
                       :width="30"
                       :height="12"
                       :data="JSON.parse(v.votes_sparkline_data)"
                       :gradient="['#333', '#333', '#333']"
                       :stroke-width="1"
                       :padding="1"
                >
                </trend>
              </div>
            </div>
          </div>
        </slide>
      </carousel>
    </b-container>

    <hr>

  </div>
</template>
