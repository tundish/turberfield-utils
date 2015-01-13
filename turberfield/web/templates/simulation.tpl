<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>{{info.get("title", "Turberfield")}}</title>
<link rel="stylesheet" href="/css/animations.css" />
<link rel="stylesheet" href="/css/pure/base-min.css" />
<link rel="stylesheet" href="/css/pure/pure-min.css" media="screen" />
<link rel="stylesheet" href="/css/pure/grids-responsive-min.css" media="screen" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
</head>
<body>
% include("gainsborough_square.tpl")

<ul data-bind="foreach: options">
  <li>
    <dl>
        <dt data-bind="text: label"></dt>
        <dd data-bind="text: value"</dd>
    </dl>
  </li>
</ul>

<script type="text/javascript" src="/js/jquery-2.1.1.js"></script>
<script type="text/javascript" src="/js/knockout-3.2.0.js"></script>
<script type="text/javascript">

var viewModel = {
    debug: ko.observable(false),
    time: ko.observable(),
    items: ko.observableArray(),
    options: ko.observableArray()
}

var checkStatus = function() {

    $.getJSON('/data/positions.json', function(data) {
        viewModel.debug(data.debug);
        viewModel.time(data.time);
        viewModel.items(data.items);
        viewModel.options(data.options);
    });


};

ko.applyBindings(viewModel);
setInterval(checkStatus, {{info.get("interval", 500)}});

</script>

</body>
</html>
