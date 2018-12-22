

$(document).ready(function() {

    $('#input_origin_salary').focus();

    $('#input_origin_salary').keyup(function() {
        var os = $(this).val();
        if(!$('#cbx_social').prop('checked')){
            $('#input_base_social_security').val(os > social_base_max ? social_base_max : (os < social_base_min ? social_base_min : os));
        }
        if(!$('#cbx_house').prop('checked')){
            $('#input_base_house_fund').val(os>house_base_max?house_base_max:os<house_base_mix?house_base_mix:os);
        }
    });

    $('#input_is_house_fund_ext').click(function(){
        if($(this).prop('checked')){
            $('#input_rate_house_fund_ext').removeAttr('disabled');
        }
        else{
            $('#input_rate_house_fund_ext').attr('disabled', 'disabled');
        }
    });

});


function calculate() {
    var sal = $('#input_origin_salary').val();
    if(!sal){
        return;
    }

    $.get(
        "/calculate",
        {
            city:'shanghai',
            origin_salary:$('#input_origin_salary').val(),
            base_social_security:$('#input_base_social_security').val(),
            base_house_fund:$('#input_base_house_fund').val(),
            is_house_fund:$('#input_is_house_fund').prop('checked'),
            is_house_fund_ext:$('#input_is_house_fund_ext').prop('checked'),
            rate_house_fund_ext:$('#input_rate_house_fund_ext > option:selected').val()
        },
        function(data){
            $('#execute').val('计算');
            $('#detail').show();
            $('#final_salary').val(data.personal_net_pay);
            $('#result').show();

            // 非法输入替换
            $('#input_origin_salary').val(data.origin_salary);
            $('#input_base_3j').val(data.base_3j);
            $('#input_base_gjj').val(data.base_gjj);
            // 明细
            $('#amt11').html(data.personal_old);
            $('#amt12').html(data.org_old);
            $('#amt21').html(data.personal_med);
            $('#amt22').html(data.org_med);
            $('#amt31').html(data.personal_unemployment);
            $('#amt32').html(data.org_unemployment);
            $('#amt41').html(data.personal_house_fund);
            $('#amt42').html(data.org_house_fund);
            $('#amt51').html(data.personal_house_fund_ext);
            $('#amt52').html(data.org_house_fund_ext);
            $('#amt62').html(data.org_work_injury);
            $('#amt72').html(data.org_birth);
            $('#amtT1').html(data.personal_prepay_deduct);
            $('#amtT2').html(data.org_pay);
            $('#amtA1').html(data.personal_taxable);
            $('#amtTx').html(data.personal_tax);
            $('#amtN').html(data.personal_net_pay);
        },
        'json'
    );
}