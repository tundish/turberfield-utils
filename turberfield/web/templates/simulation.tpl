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
% if info['refresh']:
<meta http-equiv="refresh" content="{{info['refresh']}}" />
% end
</head>
<body>
% include("gainsborough_square.tpl")

<ul data-bind="foreach: events">
  <li>
    <dl>
        <dt data-bind="text: label"></dt>
        <dd data-bind="text: deadline"</dd>
    </dl>
  </li>
</ul>

<% 
    # TODO: login form 
    opts = enumerate(options)
 %>
<ul>
    %   for n, opt in opts:
    <li><a href="#{{n}}">
    {{n}}
    </a></li>
    %   end
</ul>

<script type="text/javascript" src="/js/jquery-2.1.1.js"></script>
<script type="text/javascript" src="/js/knockout-3.2.0.js"></script>
<script type="text/javascript">

var viewModel = {
    positions: ko.observableArray(),
    events: ko.observableArray()
}

var checkPositions = function() {

    $.getJSON('/data/positions.json', function(data) {
        viewModel.positions(data.items);
    });


};

var checkEvents = function() {

    $.getJSON('/events/{{info.get("actor", "")}}', function(data) {
        viewModel.events(data.items);
    });


};

ko.applyBindings(viewModel);
setInterval(checkPositions, {{info.get("interval", 500)}});
setInterval(checkEvents, {{info.get("interval", 500)}});

</script>

</body>
</html>
