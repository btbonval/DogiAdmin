/***
 * Built-ins
 ***/

var fs = require('fs');

/***
 * functions
 ***/

function filter_options(options) {
    // take in a dictionary options.
    // look for the options "keyfile", "certfile", or "cafile".
    // for each option found, remove the option, read in the contents of the
    // file, and generate a corresponding option with the file's data.

    var preimage=['keyfile','certfile','cafile']
    var image=['key','cert','ca']
    for(var i=0; i < preimage.length; i++) {
        // check if some *file option is defined
        if (options.hasOwnProperty(preimage[i])) {
            // read in the data right now
            var data = fs.readFileSync(options[preimage[i]]);
            // remove *file option
            delete options[preimage[i]];
            // put the data into the correct option
            options[image[i]] = data.toString();
        }
    }

    return options;
}
module.exports.filter_options = filter_options;
