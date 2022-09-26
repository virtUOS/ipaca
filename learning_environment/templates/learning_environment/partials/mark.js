{% if mode == 'solve' %}
    var active_marker = $(".choosemarker").first().data('marker');
    var mark_actions={1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[]};  // which words were clicked?
    $( ".marktext span" ).on( "click", function() {
        if ($(this).hasClass("mark"+active_marker)) {  // remove marker from a word
            $(this).removeClass();
            const index = mark_actions[active_marker].indexOf($(this).data('wordcnt'));
            if (index > -1) { // only splice array when item is found
                mark_actions[active_marker].splice(index, 1); // 2nd parameter means remove one item only
            }
        } else {  // mark a word
            $(this).removeClass();
            for (var i=1; i<10; i++) {  // perhaps the word was clicked for a different marker before: remove all
                const index = mark_actions[i].indexOf($(this).data('wordcnt'));
                if (index > -1) { // only splice array when item is found
                    mark_actions[i].splice(index, 1); // 2nd parameter means remove one item only
                }
            }
            $( this ).toggleClass("mark"+active_marker);  // switch css class for marking/nonmarking
            mark_actions[active_marker].push($(this).data('wordcnt'));
        }
        $("#solution_dict").val(JSON.stringify(mark_actions));  // copy to hidden textarea for form submission
    });
    $(".choosemarker").first().toggleClass("choosemarker-chosen");
    $(".choosemarker").on("click", function () {
        $(".choosemarker-chosen").first().toggleClass("choosemarker-chosen");
        active_marker=$(this).data('marker');
        $(this).addClass("choosemarker-chosen");
    })
{% endif %}
