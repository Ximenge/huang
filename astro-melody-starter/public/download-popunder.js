(function() {
    'use strict';

    var config = {
        idzone: '5866630',
        ads_host: 'a.pemsrv.com',
        syndication_host: 's.pemsrv.com',
        frequency_period: 60,
        frequency_count: 1,
        cookie_name: 'dl_popunder_cap_5866630',
        cookieconsent: true
    };

    var CookieUtil = {
        set: function(name, value, ttl_minutes) {
            if (!config.cookieconsent) return;
            var date = new Date();
            date.setMinutes(date.getMinutes() + parseInt(ttl_minutes, 10));
            document.cookie = name + "=" + encodeURIComponent(value) + "; expires=" + date.toUTCString() + "; path=/";
        },
        get: function(name) {
            if (!config.cookieconsent) return null;
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var x = cookies[i].substr(0, cookies[i].indexOf("="));
                var y = cookies[i].substr(cookies[i].indexOf("=") + 1);
                x = x.replace(/^\s+|\s+$/g, "");
                if (x === name) return decodeURIComponent(y);
            }
            return null;
        }
    };

    function buildAdUrl() {
        var protocol = window.location.protocol === 'https:' || window.location.protocol === 'http:' ? window.location.protocol : 'https:';
        var referrer = document.referrer || window.location.href;
        var random = Math.floor(Math.random() * 1000000000);
        return protocol + "//" + config.syndication_host + "/ads-iframe-display.php?" +
            "idzone=" + config.idzone +
            "&type=8" +
            "&p=" + encodeURIComponent(referrer) +
            "&sub=" +
            "&sub2=" +
            "&sub3=" +
            "&tags=" +
            "&cat=" +
            "&el=" +
            "&pb=1" +
            "&cb=" + random;
    }

    function shouldShow() {
        var count = CookieUtil.get(config.cookie_name);
        if (!count) return true;
        var openedCount = parseInt(count.split(";")[0]) || 0;
        return openedCount < config.frequency_count;
    }

    function setAsOpened() {
        var count = CookieUtil.get(config.cookie_name);
        var openedCount = 0;
        if (count) openedCount = parseInt(count.split(";")[0]) || 0;
        openedCount++;
        var timestamp = Math.floor(Date.now() / 1000);
        CookieUtil.set(config.cookie_name, openedCount + ";" + timestamp, config.frequency_period);
    }

    window.triggerDownloadPopunder = function() {
        if (!shouldShow()) return;
        var adUrl = buildAdUrl();
        var browser = getBrowserInfo();
        if (browser.isChrome && browser.version >= 68) {
            window.open(adUrl, '_blank');
        } else {
            window.open(adUrl, '_blank', 'width=800,height=600');
        }
        setAsOpened();
    };

    function getBrowserInfo() {
        var ua = navigator.userAgent;
        var browser = { isChrome: false, version: 0 };
        if (/Chrome\/([0-9.]+)/.test(ua) && !/Edg|OPR|Brave|Vivaldi/i.test(ua)) {
            browser.isChrome = true;
            var match = ua.match(/Chrome\/([0-9]+)/);
            if (match) browser.version = parseInt(match[1]);
        }
        return browser;
    }

    function init() {
        var scriptEl = document.getElementById('download-popunderldr');
        if (scriptEl) {
            var idzone = scriptEl.getAttribute('data-idzone');
            var freqPeriod = scriptEl.getAttribute('data-frequency_period');
            var freqCount = scriptEl.getAttribute('data-frequency_count');
            if (idzone) config.idzone = idzone;
            if (freqPeriod) config.frequency_period = parseInt(freqPeriod, 10);
            if (freqCount) config.frequency_count = parseInt(freqCount, 10);
            config.cookie_name = 'dl_popunder_cap_' + config.idzone;
        }
    }

    init();
})();
