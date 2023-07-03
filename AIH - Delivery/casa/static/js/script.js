$(document).ready(function () {
    // initiale DataTable
    $('#livraison-search-table').DataTable({
        order: [],
        "pageLength": 25,
        "language": {
            "paginate": {
                "next": "Suivant",
                "previous": "Précédent"
            }
        }
    });

    $('#zones-table').DataTable({
        order: [],
        "pageLength": 25,
        "language": {
            "paginate": {
                "next": "Suivant",
                "previous": "Précédent"
            }
        }
    });


    // check selected objects 
    $('#delete').click(function () {
        var id = [];
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        $(':checkbox:checked').each(function (i) {
            id[i] = $(this).val();
        })
        if (id[0] == '0') {
            id.shift();
        }

        if (id.length === 0) {
            alert('Veuillez sélectionner des livraisons à Supprimer');
        } else {
            if (confirm('T\'es Sure baghi tmse7 hadchi ?!')) {
                $.ajax({
                    url: '.',
                    method: 'POST',
                    data: {
                        id,
                        csrfmiddlewaretoken: csrf,
                    },
                    success: function (response) {
                        for (var i = 0; i < id.length; i++) {
                            $('tr#' + id[i] + '').css('background-color', '#ccc');
                            $('tr#' + id[i] + '').fadeOut().remove(3000);
                            location.reload();
                        }
                    }
                })
            }
        }
    });


    $('#paid').click(function () {
        var ids = [];
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        $(':checkbox:checked').each(function (i) {
            ids[i] = $(this).val();
        })
        if (ids[0] == '0') {
            ids.shift();
        }
        if (ids.length === 0) {
            alert('Veuillez sélectionner des livraisons');
        } else {
            if (confirm('Marquer comme Livré ?')) {
                $.ajax({
                    url: '.',
                    method: 'POST',
                    data: {
                        ids,
                        csrfmiddlewaretoken: csrf,
                    },
                    success: function (response) {
                        for (var i = 0; i < ids.length; i++) {
                            $('tr#' + ids[i] + '').css('background-color', '#90EE90');
                            location.reload();
                        }
                    }
                })
            }
        }
    });

    $('#returned').click(function () {
        var ids_r = [];
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        $(':checkbox:checked').each(function (i) {
            ids_r[i] = $(this).val();
        })
        if (ids_r[0] == '0') {
            ids_r.shift();
        }
        if (ids_r.length === 0) {
            alert('Veuillez sélectionner des livraisons');
        } else {
            if (confirm('Marquer comme Annulé ?')) {
                $.ajax({
                    url: '.',
                    method: 'POST',
                    data: {
                        ids_r,
                        csrfmiddlewaretoken: csrf,
                    },
                    success: function (response) {
                        for (var i = 0; i < ids_r.length; i++) {
                            $('tr#' + ids_r[i] + '').css('background-color', '#F00');
                            location.reload();
                        }
                    }
                })
            }
        }
    });

    $('#pr').click(function () {
        var ids_pr = [];
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        $(':checkbox:checked').each(function (i) {
            ids_pr[i] = $(this).val();
        })
        if (ids_pr[0] == '0') {
            ids_pr.shift();
        }
        if (ids_pr.length === 0) {
            alert('Veuillez sélectionner des livraisons');
        } else {
            if (confirm('Marquer comme PR/INJ ?')) {
                $.ajax({
                    url: '.',
                    method: 'POST',
                    data: {
                        ids_pr,
                        csrfmiddlewaretoken: csrf,
                    },
                    success: function (response) {
                        for (var i = 0; i < ids_pr.length; i++) {
                            $('tr#' + ids_pr[i] + '').css('background-color', '#F00');
                            location.reload();
                        }
                    }
                })
            }
        }
    });


    $('#today').click(function () {
        var today_ids = [];
        var csrf = $('input[name="csrfmiddlewaretoken"]').val();
        $(':checkbox:checked').each(function (i) {
            today_ids[i] = $(this).val();
        })
        if (today_ids[0] == '0') {
            today_ids.shift();
        }
        if (today_ids.length === 0) {
            alert('Veuillez sélectionner des livraisons');
        } else {
            if (confirm('Vous voulez changer la date de ces livraisons à Aujourd\'hui ?')) {
                $.ajax({
                    url: '.',
                    method: 'POST',
                    data: {
                        today_ids,
                        csrfmiddlewaretoken: csrf,
                    },
                    success: function (response) {
                        for (var i = 0; i < today_ids.length; i++) {
                            $('tr#' + today_ids[i] + '').css('background-color', 'ffa500');
                            location.reload();
                        }
                    }
                })
            }
        }
    });


    document.getElementById('add_btn').style.visibility = 'hidden';
    // show Add Btn when phone is valid
    $('#id_phone').keyup(function () {
        var tel = $('#id_phone').val();
        var reg = /[0-9-+\s]/g;
        if (reg.test(tel) && tel.length > 9) {
            document.getElementById('add_btn').style.visibility = 'visible';
            document.getElementById("msg-phone").innerHTML = "Téléphone VALIDE";
            document.getElementById("msg-phone").style.background = 'lightgreen';
        } else {
            document.getElementById('add_btn').style.visibility = 'hidden';
            document.getElementById("msg-phone").innerHTML =
                "Téléphone n'est pas VALIDE - Minimum 10 numéros";
            document.getElementById("msg-phone").style.background = 'red';
        }

    });

    // Prevent non numeric char
    $('#id_phone').on('keypress', function (e) {
        return e.metaKey || // cmd/ctrl
            e.which <= 0 || // arrow keys
            e.which == 8 || // delete key
            /[0-9]/.test(String.fromCharCode(e.which)); // numbers
    })





});

// select2 to make search in a list
// Initial
$("#id_zone").select2();


// Datepicker
$('#id_start_date').datepicker({
    format: 'yyyy-mm-dd',
    todayBtn: "linked",

});
$('#id_end_date').datepicker({
    format: 'yyyy-mm-dd',
    todayBtn: "linked",

});

$('#id_created').datepicker({
    format: 'yyyy-mm-dd',
    todayBtn: "linked",

});


// Datepicker
$('#id_month_start_date').datepicker({
    format: 'yyyy-mm-dd',

});
$('#id_month_end_date').datepicker({
    format: 'yyyy-mm-dd',
});



// check all 
function select_all(source) {
    checkboxes = document.getElementsByName('selected');
    for (var i = 0, n = checkboxes.length; i < n; i++) {
        checkboxes[i].checked = source.checked;
    }
}