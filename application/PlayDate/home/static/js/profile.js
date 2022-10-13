/* profile.js
*
*   This file contains client side code to run the profile page.
*   The profile page is intended as a place for a user to edit
*   their profile and their dependents.
*   Functionality included:
*   - Make sure the state dropdown is properly selected.
*   - Dependent handling:
*       - Adding and Removing
*       - Request handling
*   The html generated by the server includes much of the data
*   in a javascript object called loadVals.
*
*   The dependent-related code is pretty robust.
*
*   The Dependent model consists of:
*   - id: The primary key of the dependent
*   - name: The name of the dependent
*   - dob: The date of birth of the dependent
*   - interests: The comma-separated interests of the dependent
*   - profile: The profile to which the dependent belongs.
*
*   Each Dependent form is controlled by a DependentControl object.
*   The DependentControl tracks:
*   -  the server side version of the dependent (dpdtCtrl.data.server)
*   -  the current client version (dpdtCtrl.data.client)
*   -  Whether dpdt is new or needs update (dpdtCtrl.state)
*   -  Whether save is needed (dpdtCtrl.visible)
*   -  The dpdtCtrl's index in its container (dpdtCtrl.id)
*   -  The suffix of ids for that dependents form controls (dpdtCtrl.suffix)
*   dpdtCtrl.generateHTML() is where each dependent generates its own form.
*
*   The DependentControls all exist inside a DependentContainer object.
*   The DependentContainer tracks each of the DependentControl and also
*   acts as a central messaging hub for events that need to interact with
*   a specific DependentControls.
*/ 

/* Enums */

// The STATE enum is used to trackwhat needs to happen server-side
// with a specific dependent.
var STATE = {
    CHANGED: "UPDATE",
    NEW: "CREATE",
    REMOVED: "DELETE"
};

/* Classes */

/* DependentControl */
//   This class controls the functionality of an individual
// dependent widget on the page. The functionality provided
// by this class includes loading from provided data, 
// collecting the inputs as JSON, and tracking what needs
// to happen server-side.
class DependentControl {

    /* dpdtCtrl() */
    // Sets up the members of the DependentControl, initializing
    // to a newly created, unsaved Dependent. depId should be the
    // index of this dpdtCtrl in the DependentContainer.
    constructor(depId) {
        this.id = depId;
        this.state = STATE.NEW;
        this.data = {
            server: {
                id: "-1",
                type: "",
                name: "",
                dob: "",
                interests: ""
            },
            client: {
                id: "-1",
                type: "",
                name: "",
                dob: "",
                interests: ""
            }
        };
        this.visible = false;
        this.suffix = "dep" + this.id;
    }

    /* dpdtCtrl.loadData() */
    // Checks the index of this dpdtCtrl in the DependentContainer
    // against the same index in the list of dependent data passed
    // from the server.
    // If there is data in the corresponding array element, we copy
    // the data into our dpdtCtrl and set the state to reflect that
    // the dependent data will be changed, not new.
    loadData() {
        if (loadVals.dependents.length > this.id) {
            this.data.client.id = this.data.server.id = loadVals.dependents[this.id].id;
            this.data.client.name = this.data.server.name = loadVals.dependents[this.id].name;
            this.data.client.type = this.data.server.type = loadVals.dependents[this.id].type;
            this.data.client.interests = this.data.server.interests = loadVals.dependents[this.id].interests;
            this.data.client.dob = this.data.server.dob = new Date(loadVals.dependents[this.id].dob);
            this.state = STATE.CHANGED;
        } 
    }

    /* dpdtCtrl.generateHTML() */
    // Dynamically collects the data in the dpdtCtrl and
    // generates an html string that can be added to the 
    // page as a div elements innerHTML. 
    // While this function formats the dependent as a 
    // form, we do not use the form submit to send the
    // data to the server. (The data is sent by AJAX)
    generateHTML() {
        var dpdtHTML = "\t\t\t\t\t<!-- Dependent "+(this.id+1)+" -->\n"
                     + "\t\t\t\t\t<form class='card mb-3' id='dep"+this.id+"Body'>\n"
                     + "\t\t\t\t\t\t<div class='card-header d-flex flex-row justify-content-between'>\n"
                     + "\t\t\t\t\t\t\t<div>Dependent "+(this.id+1)+"</div>\n"
                     + "\t\t\t\t\t\t\t<button class='btn btn-secondary ml-auto mr-3' type='button' onclick='remove("+this.id+")'>&times;</button>\n"
                     + "\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t\t<div class='card-body'>\n"
                     + loadVals.csrf.token + "\n"
                     + "\t\t\t\t\t\t\t<input type='hidden' id='dep"+this.id+"_state' name='dep_state' value='"+this.state+"'>\n"
                     + "\t\t\t\t\t\t\t<input type='hidden' id='dep"+this.id+"_dbId' name='dep_id' value='"+this.data.client.id+"'>\n"
                     + "\t\t\t\t\t\t\t<div class='col-md-10'>\n"
                     + "\t\t\t\t\t\t\t\t<label class='small mb-1' for='dep"+this.id+"_name'>Name</label>\n"
                     + "\t\t\t\t\t\t\t\t<input class='form-control' id='dep"+this.id+"_name' type='text' name='dep_name'\n"
                     + "\t\t\t\t\t\t\t\t\tplaceholder='Enter your dependents name' value='"+this.data.client.name+"' oninput='setName("+this.id+")'>\n"
                     + "\t\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t\t\t<div class='col-md-10'>\n"
                     + "\t\t\t\t\t\t\t\t<label class='small mb-1' for='dep"+this.id+"_type'>Type of Dependent</label>\n"
                     + "\t\t\t\t\t\t\t\t<select class='form-select' id='dep"+this.id+"_type' name='dep_type' value='"+this.data.client.type+"' oninput='setType("+this.id+")'>\n"
                     + "\t\t\t\t\t\t\t\t\t<option value='CHILD'>Child</option>\n"
                     + "\t\t\t\t\t\t\t\t\t<option value='PET'>Pet</option>\n"
                     + "\t\t\t\t\t\t\t\t</select>"
                     + "\t\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t\t\t<div class='col-md-10'>\n"
                     + "\t\t\t\t\t\t\t\t<label class='small mb-1' for='dep"+this.id+"_dob'>Date of Birth</label>\n"
                     + "\t\t\t\t\t\t\t\t<input class='form-control' id='dep"+this.id+"_dob' type='date' name='dep_dob'\n"
                     + "\t\t\t\t\t\t\t\t\tplaceholder='MM/DD/YYYY'  oninput='setDOB("+this.id+")'>\n"
                     + "\t\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t\t\t<div class='col-md-10'>\n"
                     + "\t\t\t\t\t\t\t\t<label class='small mb-1' for='dep"+this.id+"_interests'>Interests</label>\n"
                     + "\t\t\t\t\t\t\t\t<input class='form-control' id='dep"+this.id+"_interests' type='text' name='dep_interests'\n"
                     + "\t\t\t\t\t\t\t\t\tplaceholder='Enter your dependents interests' value='"+this.data.client.interests+"' oninput='setInterests("+this.id+")'>\n"
                     + "\t\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t\t\t<div class='col-md-10 mt-3 mr-0 ml-auto'>\n"
                     + "\t\t\t\t\t\t\t\t<button class='btn btn-primary' type='button' id='dep"+this.id+"_btn' disabled='"+(!this.visible)+"' onclick='save("+this.id+")'>Save</button>\n"
                     + "\t\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t\t</div>\n"
                     + "\t\t\t\t\t</form>\n";
        return dpdtHTML;
    }

    /* dpdtCtrl.setName() */
    // Saves the name value from the DOM to the dpdtCtrl, then 
    // affects dpdtCtrl.visible as needed through setButton()
    setName() { 
        this.data.client.name = document.getElementById(this.suffix+"_name").value; 
        this.setButton(this.data.client.name != this.data.server.name);
    }

    /* dpdtCtrl.setType() */
    // Saves the type value from the DOM to the dpdtCtrl, then 
    // affects dpdtCtrl.visible as needed through setButton()
    setType() { 
        this.data.client.type = document.getElementById(this.suffix+"_type").value; 
        this.setButton(this.data.client.type != this.data.server.type);
    }
    
    /* dpdtCtrl.setDOB() */
    // Saves the dob value from the DOM to the dpdtCtrl, then 
    // affects dpdtCtrl.visible as needed through setButton()
    setDOB() { 
        this.data.client.dob = new Date(document.getElementById(this.suffix+"_dob").value);  
        this.setButton(this.data.client.dob != this.data.server.dob);
    }
    
    /* dpdtCtrl.setInterests() */
    // Saves the interests value from the DOM to the dpdtCtrl, then 
    // affects dpdtCtrl.visible as needed through setButton()
    setInterests() { 
        this.data.client.interests = document.getElementById(this.suffix+"_interests").value;  
        this.setButton(this.data.client.interests != this.data.server.interests);
    }
    
    /* dpdtCtrl.setButton(btnVisibility) */
    // The argument represents a new value for dpdtCtrl.visible.
    // If the arg is different from the current visibility, it
    // affects the DOM accordingly and saves the new visibility.
    setButton(btnVisibility) {
        if (this.visible != btnVisibility) {
            document.getElementById("dep"+this.id+"_btn").disabled = !btnVisibility;
            this.visible = btnVisibility;
        }
    }
    
    /* dpdtCtrl.update(id) */
    // Much of how dpdtCtrl works is based on its index in the
    // DependentContainer. As such, if the index changes, we 
    // call dpdtCtrl.update(id) to adjust internally.
    update(id) {
        this.id = id;
        this.suffix = "dep"+this.id;
    }

    /* dpdtCtrl.updateWidget() */
    // Correctly sets the dob input element to reflect the dob.
    updateWidget() {
        if (this.data.client.dob instanceof Date) {
            var dobEl = document.getElementById(this.suffix+"_dob");
            dobEl.valueAsDate = this.data.client.dob;
        }
        document.getElementById(this.suffix+"_type").value = this.data.client.type;
    }
    
    /* dpdtCtrl.remove() */
    // This is the event handler for when the user clicks the X 
    // in the top-right side of the dependent form. If the dpdt
    // exists server side, we set the state of the dpdtCtrl to
    // reflect it should be deleted, then call the save() func,
    // which handles the AJAX server communication.
    remove(){
        if (this.state == STATE.CHANGED){
            this.state = STATE.REMOVED;
            document.getElementById("dep"+this.id+"_state").value = this.state;
            this.save();
            return false;
        }
        return true;
    }
    
    /* dpdtCtrl.save() */
    // Sends the dependent info up to the server using AJAX. We
    // save the id and state of the dpdtCtrl to an outside var
    // to make handling the callback easier, compile everything
    // with the appropriate headers, and send the request.
    // The callback will hit DependentContainer.transmitResponse
    save(){
        ajaxInfo.id = this.id;
        ajaxInfo.state = this.state;
        var compiledVars = {
            user: loadVals.user,
            profile: loadVals.profile,
            state: this.state,
            dependent: {
                id: this.data.client.id,
                type: this.data.client.type,
                name: this.data.client.name,
                dob: getUTC(this.data.client.dob),
                interests: this.data.client.interests
            }
        };
        let callback = function(data, status) {
            dpdtController.transmitResponse(data, status);
        }
        sendAjax(compiledVars, loadVals.dpdtURL, callback);
    }
    
    /* dpdtCtrl.parseResponse(response) */
    // Affects the dpdtCtrl according to a response from the 
    // server: 
    // If there was a server-side exception, 
    //  we send an alert to the client. 
    // If the user is not logged in, 
    //  we send them to the home page.
    // If the dependent was successfully deleted,
    //  we remove the dpdtCtrl from the DependentContainer 
    //  and notify the user.
    // If a dependent was saved to the server, either for the
    // first time or using an update,
    //  we alter the dpdtCtrl to reflect the changes
    //  and notify the user.
    parseResponse(data, status) {
        if (status == 500){
            alert("There was an error on the server.")
        } else if (status == 403) {
            window.location.replace(loadVals.homeURL);
        } else {
            if (ajaxInfo.state == STATE.REMOVED) {
                dpdtController.delete(this.id);
                setModal("Dependent Deleted", this.data.client.name + " was deleted from PlayDate.", "Ok");
                showModal();
            } else {
                this.state = STATE.CHANGED;
                this.data.server.name = this.data.client.name = data.name;
                this.data.server.type = this.data.client.type = data.type;
                this.data.server.dob = this.data.client.dob = new Date(data.dob);
                this.data.server.interests = this.data.client.interests = data.interests;
                this.data.server.id = this.data.client.id = data.id;
                this.setButton(false);
                setModal("Dependent Updated", this.data.client.name + " was updated.", "Ok");
                showModal();
            } 
        }
    }
}

/* DependentContainer */
// The container of the dependent controls.
// Acts both as a manager of the DOM container
// that holds the dpdtCtrl html, as well as
// serving as a central post office for events
// to be handed off to their appropriate dpdts.
class DependentContainer {

    /* dpdtCont(id) */
    // id is assumed to be the id of the DOM element that
    // acts as the HTML container for the dpdtCtrls.
    // We set up the dpdtCont with an empty set of dpdts.
    constructor(id) {
        this.id = id;
        this.setCount(0);
        this.dependents = [];
        this.element = document.getElementById(this.id);
    }

    /* dpdtCont.loadData() */
    // If dependents were passed down from the server, 
    // we instantiate a dpdtCtrl for each and add it to
    // our list. If no dependents exist, we instantiate
    // a fresh dpdtCtrl to be edited. Note that this does 
    // not affect the DOM.
    loadData() {
        for (var i=0; i<loadVals.dependents.length; i++) {
            this.dependents.push(new DependentControl(i));
            this.dependents[i].loadData();
        }
        this.setCount(loadVals.dependents.length);
        if (this.count == 0) {
            this.dependents.push(new DependentControl(0));
            this.setCount(1);
        }
    }

    /* dpdtCont.resetDependents() */
    // This is the function which loads the dpdtCtrls
    // into html, adds a footer at the end, and adds
    // the whole thing to the DOM. Once the dom is
    // affected, we send a message to the dpdtCtrls
    // so they can affect their dob inputs accordingly
    resetDependents() {
        var dcHTML = "";
        for (var i=0; i<this.dependents.length; i++){
            dcHTML += this.dependents[i].generateHTML();
        }
        dcHTML += "\t\t\t\t\t<!-- Dependent Footer -->\n"
            + "\t\t\t\t\t<div class='row-md-12 d-flex flex-row-reverse justify-content-between'>\n"
            + "\t\t\t\t\t\t<div class=''>\n"
            + "\t\t\t\t\t\t\t<button class='btn btn-secondary' onclick='addDependent()' >Add Dependent</button>\n"
            + "\t\t\t\t\t\t</div>\n"
            + "\t\t\t\t\t\t<div class='ml-0 mr-auto' id='depCount'>\n"
            + "\t\t\t\t\t\t\tDependents: 1\n"
            + "\t\t\t\t\t\t</div>\n"
            + "\t\t\t\t\t</div>\n"
            + "\t\t\t\t\t<!-- END: Dependent Footer -->";
        this.element.innerHTML = dcHTML;
        this.html = dcHTML;
        this.setCount(this.count);
        for (var i=0; i<this.dependents.length; i++){
            this.dependents[i].updateWidget();
        }
    }

    /* dpdtCont.setName(dpdtId) */
    // Passes priority to the correct dpdtCtrl.
    // Called by the generic setName triggered
    // by the change of the name input.
    setName(dpdtId) {
        this.dependents[dpdtId].setName();
    }

    /* dpdtCont.setType(dpdtId) */
    // Passes priority to the correct dpdtCtrl.
    // Called by the generic setType triggered
    // by the change of the name input.
    setType(dpdtId) {
        this.dependents[dpdtId].setType();
    }

    /* dpdtCont.setDOB(dpdtId) */
    // Passes priority to the correct dpdtCtrl.
    // Called by the generic setDOB triggered
    // by the change of the dob input.
    setDOB(dpdtId) {
        this.dependents[dpdtId].setDOB();
    }

    /* dpdtCont.setInterests(dpdtId) */
    // Passes priority to the correct dpdtCtrl.
    // Called by the generic setInterests triggered
    // by the change of the interests input.
    setInterests(dpdtId) {
        this.dependents[dpdtId].setInterests();
    }

    /* dpdtCont.addDependent() */
    // The event handler for a click of the 'Add Dependent'
    // button. Simply adds a fresh, empty dpdtCtrl to the
    // list.
    addDependent() {
        this.dependents.push(new DependentControl(this.count));
        this.setCount(this.count+1);
    }

    /* dpdtCont.setCount(amt) */
    // Whenever the number of dpdtCtrl's changes, we set
    // the count in our dpdtCont, and change the count text
    // in the DOM to match.
    setCount(amt) {
        this.count = amt;
        var dpdtText = this.count + " dependents";
        if (this.count == 1) {
            dpdtText = "1 dependent";
        }
        document.getElementById("depCount").innerText = dpdtText;
    }

    /* dpdtCont.save(id) */
    // Passes priority to the correct dpdtCtrl.
    save(id) { this.dependents[id].save(); }

    /* dpdtCont.remove(id) */
    // Passes the remove click to the dpdtCtrl, then
    // immediately deletes the dpdtCtrl if appropriate.
    // If the dependent existed on the server, then the
    // delete call will happen in the callback once
    // we know the dependent has been deleted.
    remove(id) { 
        if (this.dependents[id].remove()) {
            this.delete(id);
        }
    }

    /* dpdtCont.delete(id) */
    // Removes a dpdtCtrl from the dpdtCont, updates the
    // dpdtCtrls with their new indexes, then refreshes
    // the html of the entire group.
    delete(id) {
        this.dependents.splice(id,1); 
        this.setCount(this.dependents.length);
        for (var i=0; i<this.dependents.length; i++) {
            this.dependents[i].update(i);
        }
        this.resetDependents();
    }

    /* dpdtCont.transmitResponse(response) */
    // Passes priority to the correct dpdtCtrl.
    // With the AJAX callback, info is saved in 
    // the ajaxInfo variable.
    transmitResponse(data, status) {
        this.dependents[ajaxInfo.id].parseResponse(data, status);
    }
}

/* Variables */

// dpdtController: 
//   Our eventual DependentController. This does
// not get instantiated until the DOM is loaded.
var dpdtController;

// ajaxInfo:
//   Where we store data regarding the recent
// AJAX call. Includes the index of the dpdtCtrl
// that initiated the call (ajaxInfo.id), as well
// as the state of the dpdtCtrl that initiated
// the call.
var ajaxInfo = {
    id: -1,
    state: STATE.NEW
}

// The state dropdown element
var stateEl = document.getElementById("inputState");

// The gender drop down
var genderEl = document.getElementById('inputGender');

// The date of birth element
var dobEl = document.getElementById('inputDOB');

/* Event Handlers */

// remove(id)
// The event handler for the click event of the
// X in the top right of the dependent forms.
function remove(id) { dpdtController.remove(id); }

// save(id)
// The event handler for the click event of the
// save button in the bottom left of the form.
function save(id) { dpdtController.save(id); }

// setName(id)
// The event handler for the input event of the
// name input of the dependent form.
function setName(id) { dpdtController.setName(id); }

// setType(id)
// The event handler for the input event of the
// type input of the dependent form.
function setType(id) { dpdtController.setType(id); }

// setDOB(id)
// The event handler for the input event of the
// dob input of the dependent form.
function setDOB(id) { dpdtController.setDOB(id); }

// setInterests(id)
// The event handler for the input event of the
// interests input of the dependent form.
function setInterests(id) { dpdtController.setInterests(id); }

// addDependent()
// The event handler for the click event of the
// 'Add Dependent' button. Adds a dpdtCtrl, then
// resets the dependent HTML.
function addDependent() { dpdtController.addDependent(); dpdtController.resetDependents(); }

// getUTC(date)
// A function to convert a date to its UTC format
// in preperation of being sent to the server.
function getUTC(date) {
    return new Date(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate(), date.getUTCHours(),
                    date.getUTCMinutes(), date.getUTCSeconds());
}

// Validate an image
// Checks for size and file extension
// NOTE: Checking the extension of a file
//  does not guarantee that the file is
//  actually that type. 
function validateImage(inputId) {
    let imgElement = document.getElementById(inputId);
    let submittable = true;
    if (imgElement.files.length == 1) {
        imgFile = imgElement.files.item(0);
        imgSize = imgFile.size;
        imgExtension = imgFile.name.split('.').pop();
        allowedTypes = "apng,avif,gif,jpeg,jpg,png,webp";

        // Check for image too big
        if (imgSize > 6.5 * 1048578){
            imgElement.value = "";
            submitted = false;
            setModal("Image Too Large", "Your file is "+imgSize+" bytes. The max files size is "+(6.5*1048578)+" bytes. Please select another image.", "Ok");
            showModal();
        }

        // Check for proper extension
         else if (!allowedTypes.includes(imgExtension)) {
            imgElement.value = "";
            submitted = false;
            setModal("Image Wrong Type", "Your image is a "+imgExtension+" file. PlayDate only supports apng, avif, gif, jpeg, jpg, png, and webp formats. Please select another image.", "Ok");
            showModal();
        }        
    }
    return submittable;
}

// When the page loads, we need to set the state dropdown.
window.addEventListener("DOMContentLoaded", ()=> {
    // Set the state drop down to the correct state.
    stateEl.value = loadVals.profile.address.state;
    genderEl.value = loadVals.account.gender;
    dobEl.valueAsDate = new Date(loadVals.account.dob);
    // Set up the dependent controller
    dpdtController = new DependentContainer("dpdtContainer"); 
    dpdtController.loadData();
    dpdtController.resetDependents();
});