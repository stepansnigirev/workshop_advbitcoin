## Hide UI (extended functionality) with vue.js
* Let's do a toggling of the feature and unexpand by default
* let's use vue.js at the bottom of the page (to be fixed! Maybe in main-template?!):
```
<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
```
* So after that, we'll create a vue.js application which fulffills these requirements:
  * need to adjust the delimiters as the flask is using the same: ``` delimiters: ["[[", "]]"] ```
  * has data which simply shows whether the table is expanded: ``` data: { coinselection: "hidden" } ```
  * has one method which toggles from "hidden" to "visible":
```
  methods: {
        toggleExpand: function() {
			if (this.coinselectionActive =="hidden") {
				this.coinselectionActive ="visible"
			} else {
				this.coinselectionActive ="hidden"
			}
		}
   }
```
* Now modify the div to have is under control of vuejs: ``` <div id="coinselect"> ```
* add a button which will toggle: ``` <button v-on:click="toggleExpand" type="button">Expand</button> ```
* bind the table's style attribute to the value of the coinselection: ``` <table v-bind:style="{ visibility: coinselectionActive }"> ```
* Done