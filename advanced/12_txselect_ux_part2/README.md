
# Check whether selected coins are sufficient
* If someone IS selecting coins, he should/want to select all coins needed to cover the amount he want to send.
* If he doesn't do it, Core might add coins to that, which he don't want to use
* We have covered that in the unit-test in the other exercise but let's improve the UX for that requirement.
* So let's first make sure that we test that server-side and adjust the test. Add this to the end of the test:
```
    # Now let's spend more coins then we have selected. This should result in an exception:
    try:
        psbt = wallet.createpsbt(random_address, number_of_coins_to_spend +1, True, 10, selected_coins=selected_coins)
        assert False, "should throw an exception!"
    except SpecterError as e:
        pass
```
* Adjust the createpsbt-method to fullfill the adjusted test.
* Usually testing things on the serverside is better from a security-point-of-view. Implementing things client-side is more user-friendly as you can provide a better UX.
* So let's implement that now client-side and give feedback to the user much faster
* We  want:
  * if the user is unfolding coin-selection, the sum of selected coins must be more then the amount he wants to spend
  * In the case of the amount is not covered with the selected coins, the user gets an error-message and can't press the submit-button
* Let's split that work into several steps

## Migrate the list of unspent coins to Vue.js

* Add the list of unspent to the vue.js-data:
* Replace the jinja2-for-loop with a vue.js-rendered list. Hints: 
  * Do not focus too much on the features you have in the jinja2-list, mainly the img-tag. Deal with that later.
  * "in-attribute-rendering" is deprecated. You can not do something like ```<someTag someAttribute="[[ someData]]"```. Replace that with something like ```v-bind:someAttribute="someData"```
* This should already render properly, but now we need to bind that back to the data.

## Bind back the checkbox-checks to the data

* Now, as the list is rendered by vue-js, we need to sum up the amounts of the selected coins. 
* That's best done with a computed-section which is operating on the data.
* But that means that we need to somehow represent the tick-status of the checkbox within the data.
* This can be done with "v-model" in vue.js, even though the key is not yet existing in the data-structure
* Check whether your're successfull with that via the javascript-console. So if you have bound the "check" to an attributed called "selected", you can check the data like this: ```coinselection._data.unspents[0].selected```. It should be undefined in the beginning and true/false depending on the check

## Compute the sum of all selected coins

* It should now be easy to implement a computed property which is iterating over all selected txs and computes the sum
* If your app is called "spend_coins" and your computed function is called "selected_coins_sum", you can check your implementation by evaluating this in the console: ```spend_coins._computedWatchers.selected_coins_sum.value```

## Warning message and Disabling the submit-button

* Now, please compare that against the Amount-value in the input-box and print-out some warning if amount < selected_coins_sum.
* Hints:
  * The Amount-input-box is not (yet) managed by Vue. You have to "increase the vue-js managed area" and manage the amount as vue-js-data
  * check whether you're right by evaluating ``` spend_coins.amount ``` in the console
  * Show the error-message with a div and search in [styles.css](https://github.com/cryptoadvance/specter-desktop/blob/master/src/specter/static/styles.css#L406) for a style to use
  * Very similiar is the (de-)activation of the submit-button 
 
* Something very similiar is wanted for the submit-button. Let's disable the button if we have issues (same condition than the error-message above):
```
v-bind:disabled="amount > selected_coins_sum && coinselectionActive != 'hidden'"
```
* There is however, a change in appearance if you hover over the button. Let's get rid of that (not very nice, though):
```
button:disabled,
button[disabled]{
  border: 1px solid #999999;
  background-color: #cccccc;
  color: #666666;
}
.btn:not(.disabled):hover {  
	border: 1px solid #999999;
	background-color: #cccccc;
	color: #666666; 
}
```
