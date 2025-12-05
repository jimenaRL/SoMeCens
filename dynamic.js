/* dynamic loaded content */
function getLangResources(){
    
    /* dynamic translations */
    var es = new Array();
    var fr = new Array();

    es['works'] = "INSTALACIONES"; 
    es['research'] = "INVESTIGACIÓN"; 
    es['bio_contact'] = "BIO - CONTACTO";
    es['murs_invisibles'] = 'Muros Invisibles'
    es['synchronisation'] = 'Sincronización Caótica'
    es['immersion'] = 'Inmersión'
    es['conversations'] = 'Conversaciones'
    es['glass_ceilings'] = 'Glass Ceilings'
    
    fr['works'] = "INSTALLATIONS"; 
    fr['research'] = "RECHERCHE"; 
    fr['bio_contact'] = "BIO - CONTACT";
    fr['murs_invisibles'] = 'Murs Invisibles'
    fr['synchronisation'] = 'Synchronisation'
    fr['immersion'] = 'Immersion'
    fr['conversations'] = 'Conversations'
    fr['glass_ceilings'] = 'Glass Ceilings'

    var resources = new Array();
    resources['fr'] = fr;
    resources['es'] = es;
    
    return resources;
}

function loadContent(language, active_page){
    $("#exhibit").load(language + '/' + active_page + '.html');
}
    
function translateIndex(language){
    $("p[data-include][name$=index]").each(function(){
        $(this).text(getLangResources()[language][$(this).data('include')])
    }); 
}

function displaySubmenuWorks(display){
    $("[data-include='works']")[0].nextElementSibling.style.display = display;
}
    
function toggleSubmenuWorks(){
    content = $("[data-include='works']")[0].nextElementSibling;
    if (content.style.display === "block") {
        displaySubmenuWorks("none");
    } else {
        displaySubmenuWorks("block")
    }
}
    
$(function(){ 

    // defaults
    language = 'fr'
    active_page = "home_page"

    // load first content
    translateIndex(language);
    loadContent(language, active_page)

    // add load collapsible callbacks
    $("[data-include='works']").on("click", function(){
        active_page = $(this).data('include')
        loadContent(language, active_page);
    });
    
    // add load content callbacks except for collapsible elements and sibillings
    $("[data-include]").on("click", function(){
        active_page = $(this).data('include')
        loadContent(language, active_page);
    });
    
    // add load content callbacks
    $("[data-include]").not('.collapsible').not("[name='qindex']").on("click", function(){
        displaySubmenuWorks("none")
    });
    // add translations callbacks
    $("p[name='lng']").on("click", function(){
        language = $(this).attr('id')
        translateIndex(language, active_page)
        loadContent(language, active_page);
    });

    $("[data-include='works']").on("click", function(){
        toggleSubmenuWorks()
    });

});
