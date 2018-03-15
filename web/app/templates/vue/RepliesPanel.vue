<template id="replies">
  <div>
    <div class="action-link" @click="fetchData" v-show="!loaded">Show Replies</div>
    <div v-show="loaded">
      <b-container fluid class="repliespanel">
        <b-row v-for="comment in replies" :key="comment.permlink">
          <b-col>
            <b-container class="py-2 px-0">
              <b-row no-gutters>
                <b-col cols="auto">
                  <b-img-lazy :src="'https://steemitimages.com/u/' + comment.author + '/avatar/small'" rounded="circle" blank-color="#777" style="width:40px;height:40px"/>
                </b-col>
                <b-col>
                  <b-container fluid>
                    <b-row>
                      <b-col>
                        <a :href="'https://steemit.com/@' + comment.author"><b v-text="comment.author"></b></a> - {{ comment.age_string }} - {{ comment.payout_string }}
                      </b-col>
                    </b-row>
                    <b-row>
                      <b-col>
                        <div v-html="comment.body"></div>
                      </b-col>
                    </b-row>
                    <b-row>
                      <b-col>
                        <replies-panel v-if="comment.reply_count>0" :author="comment.author" :permlink="comment.permlink" :reply_count="comment.reply_count"></replies-panel>
                      </b-col>
                    </b-row>
                  </b-container>
                </b-col>
              </b-row>
            </b-container>
          </b-col>
        </b-row>
      </b-container>
    </div>
  </div>
</template>