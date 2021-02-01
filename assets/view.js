CTFd._internal.challenge.data = undefined

CTFd._internal.challenge.renderer = CTFd.lib.markdown();


CTFd._internal.challenge.preRender = function () { }

CTFd._internal.challenge.render = function (markdown) {
    return CTFd._internal.challenge.renderer.render(markdown)
}


CTFd._internal.challenge.postRender = function () { }


CTFd._internal.challenge.submit = function (preview) {
    var challenge_id = parseInt(CTFd.lib.$('#challenge-id').val());
    var variant_a = document.getElementById('challenge-variant-a').checked;
    var variant_b = document.getElementById('challenge-variant-b').checked;
    var variant_c = document.getElementById('challenge-variant-c').checked;
    var variant_d = document.getElementById('challenge-variant-d').checked;


    var body = {
        'challenge_id': challenge_id,
        'variant_a': variant_a,
        'variant_b': variant_b,
        'variant_c': variant_c,
        'variant_d': variant_d,
    }
    var params = {}
    if (preview) {
        params['preview'] = true
    }

    return CTFd.api.post_challenge_attempt(params, body).then(function (response) {
        if (response.status === 429) {
            // User was ratelimited but process response
            return response
        }
        if (response.status === 403) {
            // User is not logged in or CTF is paused.
            return response
        }
        return response
    })
};

