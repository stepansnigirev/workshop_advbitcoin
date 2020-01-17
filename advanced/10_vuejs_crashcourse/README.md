
# CoinSelection UI/UX optimized
All the improvements in this chapter will be done with the help of vue.js. We're not assuming you have any knowledge about vue.js. So let's have a crashcourse in vue.js first

## Crash Course in vue.js (Exercise in "Command and Contemplation")
* copy these lines somewhere in controller.py
```
@app.route('/vuejs/crashcourse/', methods=['GET'])
def vuejs_crashcourse():
    return render_template("vuejscrashcourse.html", some_Value="Hello Vue.js", some_array=["one","two","three"])
```
* Create a new file in src/specter/templates/vuejscrashcourse.html with this content:
```
{% extends "base.html" %}
Have a look in base.html. It consists of several blocks which we can override.<br> 
The main usecase is probably to override the block main:<br> 
{% block main %}

flask is using jinja2-templating. We render values like this:<br><br> 
{{ some_Value }}<br> <br> 
<br> <br> 
We have control-flow like this:<br> 
{% if not some_bool %} 
    Something<br> <br> 
{% else %}
    Something else<br> <br> 
{%endif %}


Vue.js uses the same delimeters for rendering values then flask: double curly brackets<br> 
For heaven sake one can change that. See the delimiter-stance below.<br> <br> 

So vue-js manages a specific part of the html-page that's marked with an id defined via "el" in the definition of the VUE-app (see below).<br> <br> 
<br> <br> 
<div id="app">
    We can now render stuff from the data-section (which will get rendered by jinja2):<br> 
    * some_bool: [[some_bool]]<br> 
    * some_array: [[some_array]]<br> 
    * but also computed values:
    [[some_computed_value]]

    You can have buttons which call methods:<br> 
    <button v-on:click="some_method" type="button">Coinselection</button>
    Here is an example of rendering an array via an implicit loop. <br>
    We can loop back the status of the checkbox in the data by "v-model" and "v-bind:value"<br>
    The change of the data is immediately reflexted in rendering.<br>
    <div v-for="x in some_array">
        <input type="checkbox" v-model="x.selected" v-bind:value="x" >[[ x ]]</input>
    </div>
    End of crashcourse.

</div>

<script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
<script>
var app = new Vue({
	el: '#app',
	delimiters: ["[[", "]]"],
	data: {
		some_array: {{ some_array|tojson }},
		some_bool: {{ some_bool|tojson }},
	},
	computed: {
		some_computed_value: function () {
            return this.some_array.reverse()
        }
	},
	methods: {
        some_method: function() {
			alert("Hello!")
		}
   }

})
</script>

{% endblock %}
```
* Contemplate about what you just have created!
* Delete it not yet, you might need it later