
// Fleshing out pineapple.js is left as an exercise for the reader


// Target Calculation:
// simple anchor calculation borrowed from iiif.io's spec anchoring

window.onload = function() {
  anchors.options.placement = 'left';
  anchors.add();
};

// update the hash fragment as we scroll
$(document).bind('scroll', function(e) {
  $('h2,h3,h4').each(function() {
    if ($(this).offset().top < window.pageYOffset + 5 && $(this).offset().top + $(this).height() > window.pageYOffset + 5) {
      var urlId = '#' + $(this).attr('id');
      window.history.replaceState(null, null, urlId);
      // This could just go to a variable to be read
    }
  });
});

// Writer:
// Build a UI that creates an annotation, 
// with target of the anchor, and TextualBody from user

// Reader:
// Build a reader that checks anchor, and does a target search
// Then read the pages into a sidebar or slideout tray


