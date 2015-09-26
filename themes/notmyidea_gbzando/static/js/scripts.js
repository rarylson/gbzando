/* GBzando scripts */

(function() {

/**
 * Trigger jQuery mobile screen events
 *
 * Check the viewport size to discover if the device has a mobile screen or not. Then, trigger a
 * proper event. If the screen is resized, the check will be done again.
 *
 * The jQuery events will be trigged by the window DOM object. The possible events are:
 *
 * - 'mobile:false': Not a mobile screen (big screen);
 * - 'mobile:true': A mobile screen.
 *
 * As some JS code can be interested in the triggered events, it's recomended to run this function
 * only after all of the other JS code.
 */
function gbzando_mobile_events() {
    var mobile_limit = 768;

    var is_mobile = ($(window).width() > mobile_limit) ? false : true;

    // Register mobile event triggering
    $(window).resize(function() {
        if (is_mobile && $(window).width() > mobile_limit) {
            is_mobile = false;
            $(window).trigger("mobile:false");
        } else if ((! is_mobile) && $(window).width() <= mobile_limit) {
            is_mobile = true;
            $(window).trigger("mobile:true");
        }
    });
    // First mobile event trigger
    $(window).trigger("mobile:" + is_mobile);
}

window.gbzando_mobile_events = gbzando_mobile_events;

})();
