google.load("mootools", "1.2.4");

var fu = {
    init: function() {
        if(is_mobile) {
            setTimeout("window.scrollTo(0,1);",100);
        }
    },
    
    notify: {
        
        noticeIsOpen: false,
        errorIsOpen: false,
        
        noticeQueue: [],
        errorQueue: [],
        
        openNotice: function(message, timeout) {
            if (this.noticeIsOpen) {
                this.noticeQueue.push([message, timeout]);
            } else {
                if (is_mobile) {
                    window.scrollTo(0,1);
                }
                
                this.noticeIsOpen = true;
                $('notifier-notice').set('text', message);
                $('notifier-notice').tween('top', "15px");
                this.closeNotice.delay(timeout, this);
            }
        },
        
        nextNotice: function() {
            this.noticeIsOpen = false;
            $('notifier-notice').set('tween', {});
            if(this.noticeQueue.length) {
                next_notice = this.noticeQueue.shift();
                this.openNotice(next_notice[0], next_notice[1]);
            }
        },
        
        closeNotice: function() {
            $('notifier-notice').set('tween', {
                'onComplete': function() {
                    $('notifier-notice').set('text', '');
                    this.nextNotice();
                }.bind(this)
            });
            $('notifier-notice').tween('top', "-50px");
        },
        
        openError: function(message, timeout) {
            if (this.errorIsOpen) {
                this.errorQueue.push([message, timeout]);
            } else {
                if (is_mobile) {
                    window.scrollTo(0,1);
                }
                
                this.errorIsOpen = true;
                (this.noticeIsOpen) ? toTop = "50px" : toTop = "15px";
                $('notifier-error').set('text', message);
                $('notifier-error').tween('top', toTop);
                this.closeError.delay(timeout, this);
            }
        },
        
        nextError: function() {
            this.errorIsOpen = false;
            $('notifier-error').set('tween', {});
            if(this.errorQueue.length) {
                next_notice = this.errorQueue.shift();
                this.openError(next_notice[0], next_notice[1]);
            }
        },
        
        closeError: function() {
            $('notifier-error').set('tween', {
                'onComplete': function() {
                    $('notifier-error').set('text', '');
                    this.nextError();
                }.bind(this)
            });
            $('notifier-error').tween('top', "-50px");
        },
        
        fire: function(message, type, timeout) {
            (typeof(type) == "undefined") ? type = "notice" : null;
            (typeof(timeout) == "undefined") ? timeout = 4000 : null;
            switch(type) {
                case "notice":
                    this.openNotice(message, timeout);
                    break;
                case "error":
                    this.openError(message, timeout);
            }
        }
    }
}

google.setOnLoadCallback(function() {
    window.addEvent('domready', function() {
        fu.init();
    });
});