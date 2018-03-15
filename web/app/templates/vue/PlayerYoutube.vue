<template id="player-youtube">
  <div>
    <div style="position:relative" id="playerholder">
      <div id="player"></div>
      <div v-if="overlay" id="playeroverlay" style="background: rgba(100,100,100, 0.5); position:absolute; top:0; left:0; width:100%;height:99%; z-index:16777271;"></div>
      <!--
      <button style="position:absolute; top:0; left:0; width:20;height:20;z-index:16777271;" @click="overlay=!overlay">C</button>
      //-->
    </div>
  </div>    
</template>