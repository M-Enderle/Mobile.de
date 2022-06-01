let currently_predicted = {};

function select_color(color) {
    $('.color-preview').removeClass('selected');
    $("#"+color+" > .color-preview").addClass("selected");
    $("#color-input").val(color);
    check_filled();
}


$(function(){
    var requiredCheckboxes = $('.car-type :checkbox[required]');
    requiredCheckboxes.change(function(){
        if(requiredCheckboxes.is(':checked')) {
            requiredCheckboxes.removeAttr('required');
        } else {
            requiredCheckboxes.attr('required', 'required');
        }
    });

    let in_ = $('input')
    let sel_ = $('select')
    in_.focusout(function(){
        closest();
    });
    sel_.focusout(function(){
        closest();
    });
    in_.focusin(function(){
        $(this).removeClass('auto-filled');
    });
    sel_.focusin(function(){
        $(this).removeClass('auto-filled');
    });

    $('#manufacturer').change(function(){
        $("input").not("#model").val("");
        $("select").not("#manufacturer").val("");
        $('.color-preview').removeClass('selected');
        $('input:checkbox').prop('checked', false);
    });

    in_.change(check_filled);
    sel_.change(check_filled);
});


function check_filled(){
    let all_inp = $("input").not(".checkbox").filter(function () {
        return $.trim($(this).val()).length === 0
    }).length === 0;

    let all_sel= $("select").filter(function () {
        return $.trim($(this).val()).length === 0
    }).length === 0;

    let checkbox_checked = $('.car-type :checkbox:checked').length > 0;

    if(all_inp && all_sel && checkbox_checked){
        predict();
    }
}



function autofill(title){
    let car_info = currently_predicted[title];
    const attributes = {"first_registration":"Erstzulassung", "power":"Leistung", "cubicCapacity":"Hubraum", "consumption":"Verbauch", "co2":"CO₂",
                        "fuel":"Treibstoff", "climate_control":"Klimaanlage", "gear":"Getriebe", "airbag":"Airbag", "environment_class":"Umweltplakette",
                        "emission_class":"Schadstoffklasse", "doors":"Türen", "num_seats":"Sitze"};

    for (const [key, value] of Object.entries(attributes)) {
        let el = $("#"+key);
        if (el.val() === "" || el.hasClass("auto-filled")) {
            el.val(car_info[key]);
            el.addClass("auto-filled");
        }
    }
}


function closest(){
    const manufacturer = $("#manufacturer").val().toLowerCase();
    const model = $("#model").val().toLowerCase();

    if(manufacturer.length === 0 && model.length === 0){
        return;
    }

    let data = {
            "manufacturer": manufacturer,
            "model": model,
            "num_seats": "",
            "doors": "",
            "first_registration": "",
            "power": "",
            "cubicCapacity": "",
            "fuel": "",
            "gear": "",
            "consumption": "",
            "co2": "",
            "emission_class": "",
            "airbag": "",
            "climate_control": "",
            "environment_class": ""
        }

    let to_int = ["environment_class", "emission_class", "doors", "num_seats"];
    for (const [key, value] of Object.entries(data)) {
        let el = $("#"+key);
        if (el.val() !== "" && !el.hasClass("auto-filled")) {
            data[key] = el.val().toLowerCase();
            if(to_int.includes(key)){
                data[key] = parseInt(data[key]);
            }
        }
    }

    fetch('/closest', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json()).then((responseJson) => {
        if(responseJson.status === "ok") {

            $(".similar-cars").empty();

            if(responseJson.data !== null) {

                currently_predicted = {};

                responseJson.data.forEach(function(car){

                    currently_predicted[car.title] = car;

                    let url = "/static/images/not_found.png";
                    if(car.img_url !== null){
                        url = car.img_url;
                    }
                    $(".similar-cars").append(
                        `<div class="similar-car" title="Daten automatisch ausfüllen" onclick="autofill('${car.title}');">
                            <div class="similar-row">
                                <div class="preview-image" style="background-image: url('${url}');"></div>
                            </div>
                            <div class="similar-row">
                                <a class="car-title" target="_blank" title="Auto auf mobile.de öffnen" href="${car.url}">${car.title}</a>
                            </div>
                        </div>`
                    );
                    let lastSimilarCar = $(".similar-car").last();

                    const attributes = {"first_registration":"Erstzulassung", "power":"Leistung", "cubicCapacity":"Hubraum", "consumption":"Verbauch", "co2":"CO₂",
                        "fuel":"Treibstoff", "climate_control":"Klimaanlage", "gear":"Getriebe", "airbag":"Airbag", "environment_class":"Umweltplakette",
                        "emission_class":"Schadstoffklasse", "doors":"Türen", "num_seats":"Sitze"};

                    car.consumption = car.consumption.toFixed(2);

                    for (const [key, value] of Object.entries(attributes)) {
                        if(car[key] !== null){
                            lastSimilarCar.append(
                                `<div class="stat-row">
                                    <div class="stat-name">${value}:</div>
                                    <div class="stat-value">${car[key]}</div>
                                </div>`
                            );
                        }
                    }
                });
            } else {
                $(".similar-cars").append(`
                <div class="stat-row">
                    <div class="stat-value">Keine ähnlichen Autos gefunden</div>
                </div>
                
                `);
            }
        }
    });

}


function predict(){
    const manufacturer = $("#manufacturer").val().toLowerCase();
    const model = $("#model").val().toLowerCase();
    let car_types = [];
    const num_seats = $("#num_seats").val().toLowerCase();
    const doors = $("#doors").val().toLowerCase();
    const num_of_owners = $("#num_of_owners").val().toLowerCase();
    const condition = $("#condition").val().toLowerCase();
    const first_registration = $("#first_registration").val().toLowerCase();
    const hu = $("#hu").val().toLowerCase();
    const mileage = $("#mileage").val().toLowerCase();
    const power = $("#power").val().toLowerCase();
    const cubicCapacity = $("#cubicCapacity").val().toLowerCase();
    const fuel = $("#fuel").val().toLowerCase();
    const gear = $("#gear").val().toLowerCase();
    const consumption = $("#consumption").val().toLowerCase();
    const co2 = $("#co2").val().toLowerCase();
    const emission_class = $("#emission_class").val().toLowerCase();
    const airbag = $("#airbag").val().toLowerCase();
    const climate_control = $("#climate_control").val().toLowerCase();
    const interior = $("#interior").val().toLowerCase();
    const color = $("#color-input").val().toLowerCase();
    const environment_class = $("#environment_class").val().toLowerCase();

    $('.car-type :checkbox').each(function(){
        if($(this).is(':checked')){
            car_types.push($(this).attr('name'));
        }
    });

    fetch('/predict', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "manufacturer": manufacturer,
            "model": model,
            "car_types": car_types,
            "num_seats": num_seats,
            "doors": doors,
            "num_of_owners": num_of_owners,
            "condition": condition,
            "first_registration": first_registration,
            "hu": hu,
            "mileage": mileage,
            "power": power,
            "cubicCapacity": cubicCapacity,
            "fuel": fuel,
            "gear": gear,
            "consumption": consumption,
            "co2": co2,
            "emission_class": emission_class,
            "airbag": airbag,
            "climate_control": climate_control,
            "interior": interior,
            "color": color,
            "environment_class": environment_class
        })
    }).then(response => response.json()).then((responseJson) => {
        if(responseJson.status === "ok") {
            $(".predicted-price").text(parseFloat(responseJson.price).toFixed(2) + "€");
            $(".price-bounds.lower").text((parseFloat(responseJson.price) - parseFloat(responseJson.price) * (0.07924108/2)).toFixed(2) + "€")
            $(".price-bounds.higher").text((parseFloat(responseJson.price) + parseFloat(responseJson.price) * (0.07924108/2)).toFixed(2) + "€")
        }
    });
}

