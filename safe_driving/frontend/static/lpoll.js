
var prev_data = null;           // remember data fetched last time
var waiting_for_update = false; // are we currently waiting?
var LONG_POLL_DURATION = 60000; // how long should we wait? (msec)


/**
 * Load data from /data, optionally providing a query parameter read
 * from the #format select
 */
function load_data() {
    var url = '/monitor';
    $.ajax({url:     url,
            success: function(data) {
                console.log(data)
                display_data(data);
                wait_for_update();
            }
    });
    return true;
}


/**
 * Uses separate update notification and data providing URLs. Could be combined, but if
 * they're separated, the Python routine that provides data needn't be changed from
 * what's required for standard, non-long-polling web app. If they're combined, arguably
 * over-loads the purpose of the function.
 */
function wait_for_update() {
    if (!waiting_for_update) {
        waiting_for_update = true;
        $.ajax({ url: '/updated',
                 success:  load_data,        // if /update signals results ready, load them!
                 complete: function () {
                    waiting_for_update = false;
                    wait_for_update(); // if the wait_for_update poll times out, rerun
                 },
                 timeout:  LONG_POLL_DURATION,
               });
    }

    // wait_for_update guard to ensure not re-entering already running wait code
    // added after user suggestion. This check has not been needed in my apps
    // and testing, but concurrency is an area where an abundance of caution is
    // often the best policy.
}


/**
 * show the data acquired by load_data()
 */
function display_data(data) {
    if (data) {
    // if there is data, and it's changed

        // update the contents of several HTML divs via jQuery
        $('div#head').text("Looking Forward: " + data.Looking_Forward);
        $('div#eye').text("Eye Open: " + data.Eye_Open);
        $('div#phone').text("Phone Up: " + data.Phone_Up);
        $('div#warning').text(data.Warning? "Warning!" : "");

        // a little UI sparkle - show the #updated div, then after a little
        // while, fade it away
        $('#updated').fadeIn('fast');
        setTimeout(function() {  $('#updated').fadeOut('slow');  }, 2500);
    }
}

/**
 * Initial document setup - hide the #updated message, and provide a
 * "loading..." message
 */
$(document).ready(function() {
    $('div#updated').fadeOut(0);
    $('div#contents').append('awaiting data...');

    // load the initial data (assuming it will be immediately available)
    load_data();
});
