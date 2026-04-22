/**
 * Popunder 广告系统 - 简化版
 * 基于 ExoClick 原理实现
 */
(function() {
    'use strict';
    
    // 配置 - 基于 pp.md 中的 ExoClick 配置
    var config = {
        idzone: '5866630',                // 广告位ID
        ads_host: 'a.pemsrv.com',         // 广告主机
        syndication_host: 's.pemsrv.com', // 同步主机
        frequency_period: 60,             // 频率限制周期（分钟）
        frequency_count: 1,               // 周期内最多显示次数（1小时1次）
        trigger_method: 1,                // 触发方式：1=任意点击
        trigger_class: '',                // 触发class
        trigger_delay: 0,                 // 触发延迟（秒）
        cookie_name: 'popunder_cap_5866630',
        capping_enabled: true,            // 启用频率限制
        chrome_enabled: true,             // Chrome浏览器启用
        new_tab: false,                   // 是否在新标签页打开
        popup_fallback: false,            // 弹窗回退
        popup_force: false,               // 强制弹窗
        tcf_enabled: true,                // TCF 同意框架
        only_inline: false,               // 仅内联
        cookieconsent: true               // 需要Cookie同意
    };
    
    // Cookie 操作
    var CookieUtil = {
        set: function(name, value, ttl_minutes) {
            if (!config.cookieconsent) return false;
            var date = new Date();
            date.setMinutes(date.getMinutes() + parseInt(ttl_minutes, 10));
            var c_value = encodeURIComponent(value) + "; expires=" + date.toUTCString() + "; path=/";
            document.cookie = name + "=" + c_value;
        },
        
        get: function(name) {
            if (!config.cookieconsent) return null;
            var cookies = document.cookie.split(";");
            for (var i = 0; i < cookies.length; i++) {
                var x = cookies[i].substr(0, cookies[i].indexOf("="));
                var y = cookies[i].substr(cookies[i].indexOf("=") + 1);
                x = x.replace(/^\s+|\s+$/g, "");
                if (x === name) {
                    return decodeURIComponent(y);
                }
            }
            return null;
        }
    };
    
    // 获取广告URL - 基于 ExoClick 格式
    function buildAdUrl() {
        var protocol = window.location.protocol;
        if (protocol !== 'https:' && protocol !== 'http:') {
            protocol = 'https:';
        }
        var referrer = document.referrer || window.location.href;
        var random = Math.floor(Math.random() * 1000000000);
        
        // 构建 ExoClick 格式的广告 URL
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
    
    // 检查是否应该显示广告
    function shouldShow() {
        if (!config.capping_enabled) {
            return true;
        }
        
        var count = CookieUtil.get(config.cookie_name);
        if (!count) {
            return true;
        }
        
        var parts = count.split(";");
        var openedCount = parseInt(parts[0]) || 0;
        
        return openedCount < config.frequency_count;
    }
    
    // 记录广告已显示
    function setAsOpened() {
        if (!config.capping_enabled) return;
        
        var count = CookieUtil.get(config.cookie_name);
        var openedCount = 0;
        
        if (count) {
            var parts = count.split(";");
            openedCount = parseInt(parts[0]) || 0;
        }
        
        openedCount++;
        var timestamp = Math.floor(Date.now() / 1000);
        CookieUtil.set(config.cookie_name, openedCount + ";" + timestamp, config.frequency_period);
    }
    
    // 浏览器检测
    function getBrowserInfo() {
        var ua = navigator.userAgent;
        var browser = {
            name: 'other',
            version: 0,
            isChrome: false,
            isMobile: /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(ua)
        };
        
        // 检测 Chrome
        if (/Chrome\/([0-9.]+)/.test(ua) && !/Edg|OPR|Brave|Vivaldi/i.test(ua)) {
            browser.isChrome = true;
            browser.name = 'chrome';
            var match = ua.match(/Chrome\/([0-9]+)/);
            if (match) {
                browser.version = parseInt(match[1]);
            }
        }
        
        return browser;
    }
    
    // 弹窗方法
    var PopMethods = {
        // 默认方法：直接打开
        default: function(e) {
            if (!shouldShow()) return true;
            
            var adUrl = buildAdUrl();
            var target = e.target || e.srcElement;
            var originalUrl = target.href || window.location.href;
            
            // 在新标签页打开原链接
            window.open(originalUrl, '_blank');
            
            // 在当前页打开广告
            window.location.href = adUrl;
            
            setAsOpened();
            
            if (e.preventDefault) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            return false;
        },
        
        // Chrome 方法：使用 Ctrl+点击
        chromeTab: function(e) {
            if (!shouldShow()) return true;
            
            if (e.preventDefault) {
                e.preventDefault();
                e.stopPropagation();
            } else {
                return true;
            }
            
            var adUrl = buildAdUrl();
            var target = e.target || e.srcElement;
            var originalUrl = target.href || window.location.href;
            
            // 创建临时链接元素
            var a = document.createElement('a');
            a.href = originalUrl;
            document.body.appendChild(a);
            
            // 模拟 Ctrl+点击打开原链接
            var event = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window,
                ctrlKey: true,
                metaKey: true,
                button: 0
            });
            a.dispatchEvent(event);
            a.parentNode.removeChild(a);
            
            // 在当前页打开广告
            window.open(adUrl, '_self');
            
            setAsOpened();
            
            return false;
        },
        
        // 弹窗方法
        popup: function(e) {
            if (!shouldShow()) return true;
            
            var adUrl = buildAdUrl();
            var target = e.target || e.srcElement;
            var originalUrl = target.href || window.location.href;
            
            // 打开弹窗
            var popup = window.open(originalUrl, '_blank', 'width=800,height=600');
            
            // 在当前页打开广告
            setTimeout(function() {
                window.location.href = adUrl;
            }, 200);
            
            setAsOpened();
            
            if (e.preventDefault) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            return false;
        }
    };
    
    // 获取弹窗方法
    function getPopMethod(browser) {
        if (config.new_tab) {
            return PopMethods.chromeTab;
        }
        if (browser.isMobile) {
            return PopMethods.default;
        }
        if (browser.isChrome && browser.version >= 68) {
            return PopMethods.chromeTab;
        }
        return PopMethods.default;
    }
    
    // 添加事件监听
    function addEvent(element, event, handler) {
        if (element.addEventListener) {
            element.addEventListener(event, handler, false);
        } else if (element.attachEvent) {
            element.attachEvent('on' + event, handler);
        } else {
            element['on' + event] = handler;
        }
    }
    
    // 获取触发元素
    function getTriggerElements() {
        var method = parseInt(config.trigger_method);
        
        switch(method) {
            case 1: // 任意点击
                return [document];
            case 2: // 特定class
                if (!config.trigger_class) return [document];
                var classes = config.trigger_class.split(',');
                var elements = [];
                classes.forEach(function(cls) {
                    var elems = document.querySelectorAll('.' + cls.trim());
                    elements = elements.concat(Array.prototype.slice.call(elems));
                });
                return elements.length ? elements : [document];
            case 3: // 点击链接
                return Array.prototype.slice.call(document.querySelectorAll('a'));
            case 4: // 非特定class
                return [document];
            case 5: // 非链接
                return [document];
            default:
                return [document];
        }
    }
    
    // 事件处理
    function handleClick(e) {
        var browser = getBrowserInfo();
        
        // 检查 Chrome 启用设置
        if (browser.isChrome && !config.chrome_enabled) {
            return true;
        }
        
        var method = getPopMethod(browser);
        return method(e);
    }
    
    // 初始化
    function init() {
        // 从 script 标签读取配置
        var scriptEl = document.getElementById('popunderldr');
        if (scriptEl) {
            var attrs = scriptEl.attributes;
            for (var i = 0; i < attrs.length; i++) {
                var attr = attrs[i];
                if (attr.name.indexOf('data-') === 0) {
                    var key = attr.name.replace('data-', '');
                    var value = attr.value;
                    
                    // 类型转换
                    if (config.hasOwnProperty(key)) {
                        var currentType = typeof config[key];
                        if (currentType === 'number') {
                            config[key] = parseInt(value, 10);
                        } else if (currentType === 'boolean') {
                            config[key] = value === 'true';
                        } else {
                            config[key] = value;
                        }
                    }
                }
            }
        }
        
        // 设置 cookie 名称
        config.cookie_name = 'popunder_cap_' + config.idzone;
        
        // 等待页面加载完成
        if (document.readyState === 'complete') {
            bindEvents();
        } else {
            addEvent(window, 'load', bindEvents);
        }
    }
    
    // 绑定事件
    function bindEvents() {
        var elements = getTriggerElements();
        var handler = function(e) {
            // 检查触发条件
            var method = parseInt(config.trigger_method);
            var target = e.target || e.srcElement;
            
            if (method === 4 && config.trigger_class) {
                // 非特定class
                var classes = config.trigger_class.split(',');
                for (var i = 0; i < classes.length; i++) {
                    if (target.closest('.' + classes[i].trim())) {
                        return true;
                    }
                }
            }
            
            if (method === 5) {
                // 非链接
                if (target.tagName === 'A' || target.closest('a')) {
                    return true;
                }
            }
            
            return handleClick(e);
        };
        
        elements.forEach(function(el) {
            addEvent(el, 'click', handler);
        });
    }
    
    // 启动
    init();
    
})();
