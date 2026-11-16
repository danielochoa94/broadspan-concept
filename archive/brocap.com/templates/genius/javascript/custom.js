jQuery(document).ready(function() {

    function menuSelect(){
        jQuery('#header #logo').after("<div class='selected_menu' style='display:none'><select size='1'></select></div>");
        jQuery('.selected_menu select').attr('onchange','location = this.options[this.selectedIndex].value;')
        jQuery( ".nav.menu a:not(.back_to_menu)" ).each(function() {
            var link = jQuery(this).attr('href');
            var link_title = jQuery( this ).text();
            var options = "<option value='"+link+"'>"+link_title+"</option>";
            jQuery('.selected_menu select').append(options);
        });
        var parametr = window.location.pathname;
        jQuery('.selected_menu select option').each(function(){
            var selectValue = jQuery(this).val();
            if (selectValue === parametr) {
                jQuery(this).attr('selected', true);
            }
        });
    }
/*    var windowHeight = jQuery(window).height();
    jQuery('.slider_bg>.span12').height(windowHeight);
    jQuery(window).load(function() {
        var galMargTop = jQuery('.six_gallery_container>li:first-child').height();
        jQuery('#portfolio .six_imageGallery').css('margin-top',-galMargTop)
    });
*/
    function menuSelectResize(){
        var widthWindow = jQuery(window).width();
        if (widthWindow <= 1024) {
            jQuery('.selected_menu').css('display','block');
            jQuery('.main_menu').css('display','none');

        } else{
            jQuery('.selected_menu').css('display','none');
            jQuery('.main_menu').css('display','block');
        }
    }
    menuSelect();
    menuSelectResize();

    jQuery(".bottom_arrow.anchor").click(function(){
        jQuery('html, body').animate({
            scrollTop: jQuery( jQuery.attr(this, 'href')).offset().top
        }, 'slow');
        return false;
    });

    function headerSize(e) {
        if (jQuery("#header")) {
            if (e >= 0 && e <= 45) {
				jQuery("#logobsam").css("line-height", 110-e+"px");/* your custom id */
                jQuery("#logo").css("line-height", 110-e+"px");
                jQuery(".soc_icons_box .soc_icons a").css("line-height", 110-e+"px");
                jQuery("#header .span7.main_menu .nav.menu>li>a").css("line-height", 110-e+"px");
            } else if (e > 45) {
                jQuery("#logo").css("line-height", "65px");
                jQuery(".soc_icons_box .soc_icons a").css("line-height", "65px");
                jQuery("#header .span7.main_menu .nav.menu>li>a").css("line-height", "65px");
				jQuery("#logobsam").css("line-height", "65px");/* your custom id */ 
            }
        }
    }
    $scroll = jQuery(window).scrollTop();
    headerSize($scroll);
    jQuery(window).scroll(function () {
        $scroll = jQuery(window).scrollTop();
        headerSize($scroll);
    });

    function initCounter() {
        jQuery('.counter').each(function () {
            jQuery(this).appear(function () {
                jQuery(this).absoluteCounter({
                    speed: 1500,
                    fadeInDelay: 1000
                })
            })
        })
    };
    initCounter();


    var heightFooter = jQuery( "#footer" ).height()+100;
    jQuery( "#main" ).css('padding-bottom', heightFooter+'px');
    
    jQuery('button').addClass('btn');

  /*  jQuery(window).resize(function(){
        menuSelectResize();
        var windowHeight = jQuery(window).height();
        jQuery('.slider_bg>.span12').height(windowHeight);
        var heightFooter = jQuery( "#footer" ).height()+100;
        jQuery( "#main" ).css('padding-bottom', heightFooter+'px'); 
    });
*/
});

jQuery(function() { 
jQuery('a[href^="#"]').click(function(){ 
var el = jQuery(this).attr('href'); 
jQuery('body').animate({ 
scrollTop: jQuery(el).offset().top}, 1000); 
return false; 
}); 
}); 