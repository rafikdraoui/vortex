(function () {
    'use strict';

    /* We can access this variable if we need to clear the
     * update_display timeout. */
    var update_timeout;

    /* Return the html for div#song-info. The input is a json object
     * describing the state of the music player. */
    function get_song_info_html(info) {
        var song = info.song;
        var html = '<h1>' + song.title + '</h1>';
        html +=  '<h1><small>' + song.artist + '</small></h1>';
        html += '<h5>[random: ' + (info.random ? 'on' : 'off') + '] ';
        html += '[repeat: ' + (info.repeat ? 'on' : 'off') + '] ';
        if (info.state === 'pause') {
            html += '[paused]';
        }
        else if (info.state === 'stop') {
            html += '[stopped]';
        }
        html += '</h5>';
        return html;
    }

    function update_display() {
        $.get(vortex.urls.update, function (data) {

            if (!data.success) {
                $('#error-messages').empty();
                $('#error-messages').html(
                    '<div class="alert alert-error">\n'
                  + '<button type="button" class="close" '
                  + 'data-dismiss="alert">×</button>\n'
                  + data.error + '\n</div>');
                return;
            }

            // update currently playing song information.
            $('#song-info').html(get_song_info_html(data));

            // update play-pause button according to the state.
            $('#play-pause-button > i').toggleClass(
                'icon-play', data.state !== 'play');
            $('#play-pause-button > i').toggleClass(
                'icon-pause', data.state === 'play');

            // update random and repeat buttons.
            $('#random-button').toggleClass('active', data.random);
            $('#repeat-button').toggleClass('active', data.repeat);
        });
    }

    function update_loop() {
        if (vortex.refresh_rate === 0) {
            return;
        }
        update_display();
        update_timeout = window.setTimeout(update_loop, vortex.refresh_rate);
    }

    function dispatch(url) {
        //TODO: Change to POST, take care of csrf token
        $.get(url, function () {
            update_display();
        });
    }

    function addClickHandlers() {
        $('#play-pause-button').click(function () {
            dispatch(vortex.urls.play_pause);
        });
        $('#next-button').click(function () {
            dispatch(vortex.urls.next);
        });
        $('#prev-button').click(function () {
            dispatch(vortex.urls.prev);
        });
        $('#random-button').click(function () {
            dispatch(vortex.urls.random);
        });
        $('#repeat-button').click(function () {
            dispatch(vortex.urls.repeat);
        });
    }

    $(document).ready(function () {
        addClickHandlers();
        update_display();
        if (vortex.refresh_rate !== 0) {
            update_loop();
        }
    });
}());
