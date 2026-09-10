# Remote Canvas

A minimal HTTP API for drawing on the device. Any device that can send a
POST request can use it: a script, a CI job, a home automation hook,
whatever you've got.

Start the app, then open its page (or the device IP directly) for the live
base URL and some copy-paste examples. It only holds 11 distinct colors at
once (a palette limit of the LED panel), so requesting a 12th color evicts
whichever one was used longest ago.

This is meant for occasional redraws, not heavy or continuous drawing
logic. Think a status readout, a notification, a dashboard tile that
updates every few seconds or minutes. Every route runs synchronously and
calls `refresh()` before returning, so each POST blocks until that frame is
actually on the panel. There's no batching, no animation loop, no partial
updates. Updating a scene means resending the whole thing, one request per
shape, same as the examples below. It's a poor fit for anything driven at
high frequency, like animations, games, or live meters.

## Routes

Colors are `#RRGGBB` hex strings. Drawing is additive, nothing gets cleared
between calls, so send `/background` first if you want a clean frame.

### `GET /info`

```json
{
  "width": 64,
  "height": 32
}
```

### `POST /background`

```json
{
  "color": "#003366"
}
```

### `POST /pixel`

```json
{
  "x": 5,
  "y": 5,
  "color": "#ffffff"
}
```

### `POST /line`

```json
{
  "x0": 2,
  "y0": 2,
  "x1": 20,
  "y1": 10,
  "color": "#ffffff"
}
```

### `POST /rect`

`border_color` and `fill_color` are both optional, but give at least one.

```json
{
  "x0": 2,
  "y0": 2,
  "x1": 20,
  "y1": 10,
  "border_color": "#ffffff",
  "fill_color": "#ff0000"
}
```

### `POST /circle`

`x`/`y` is the center. `border_color` and `fill_color` are both optional,
but give at least one.

```json
{
  "x": 16,
  "y": 16,
  "radius": 8,
  "border_color": "#ffffff",
  "fill_color": "#ff0000"
}
```

### `POST /text`

`x`/`y` place the text at an exact pixel and override `align`/`valign`
entirely. `padding` nudges edge-aligned text inward (say `align: "left"`
with `padding: 2` starts 2px in from the left edge); it has no effect when
align or valign is `"center"`.

```json
{
  "text": "Hello",
  "font_size": "small",
  "color": "#ffffff",
  "align": "center",
  "valign": "center",
  "padding": 0
}
```

## Example: an 80% battery icon

Reads the panel size from `GET /info` so the battery centers correctly on
any display, then draws a fixed size icon at the computed position. Replace
`IP` with your device's address (shown on this app's `/` page).

```bash
INFO=$(curl -s http://$IP/info)
WIDTH=$(echo "$INFO" | grep -o '"width": *[0-9]*' | grep -o '[0-9]*$')
HEIGHT=$(echo "$INFO" | grep -o '"height": *[0-9]*' | grep -o '[0-9]*$')

BODY_X0=$(( (WIDTH - 46) / 2 ))
BODY_Y0=$(( 12 + ((HEIGHT - 12) - 13) / 2 ))
BODY_X1=$(( BODY_X0 + 42 ))
BODY_Y1=$(( BODY_Y0 + 12 ))
NUB_X0=$(( BODY_X0 + 43 ))
NUB_X1=$(( BODY_X0 + 45 ))
NUB_Y0=$(( BODY_Y0 + 3 ))
NUB_Y1=$(( BODY_Y0 + 9 ))

curl -s http://$IP/background -d "{\"color\":\"#000000\"}"
curl -s http://$IP/rect -d "{\"x0\":$BODY_X0,\"y0\":$BODY_Y0,\"x1\":$BODY_X1,\"y1\":$BODY_Y1,\"border_color\":\"#ffffff\",\"fill_color\":\"#000000\"}"
curl -s http://$IP/rect -d "{\"x0\":$NUB_X0,\"y0\":$NUB_Y0,\"x1\":$NUB_X1,\"y1\":$NUB_Y1,\"fill_color\":\"#ffffff\"}"
curl -s http://$IP/rect -d "{\"x0\":$((BODY_X0+2)),\"y0\":$NUB_Y0,\"x1\":$((BODY_X0+7)),\"y1\":$NUB_Y1,\"fill_color\":\"#00ff00\"}"
curl -s http://$IP/rect -d "{\"x0\":$((BODY_X0+10)),\"y0\":$NUB_Y0,\"x1\":$((BODY_X0+15)),\"y1\":$NUB_Y1,\"fill_color\":\"#00ff00\"}"
curl -s http://$IP/rect -d "{\"x0\":$((BODY_X0+18)),\"y0\":$NUB_Y0,\"x1\":$((BODY_X0+23)),\"y1\":$NUB_Y1,\"fill_color\":\"#00ff00\"}"
curl -s http://$IP/rect -d "{\"x0\":$((BODY_X0+26)),\"y0\":$NUB_Y0,\"x1\":$((BODY_X0+31)),\"y1\":$NUB_Y1,\"fill_color\":\"#00ff00\"}"
curl -s http://$IP/rect -d "{\"x0\":$((BODY_X0+34)),\"y0\":$NUB_Y0,\"x1\":$((BODY_X0+39)),\"y1\":$NUB_Y1,\"border_color\":\"#ffffff\"}"
curl -s http://$IP/text -d '{"text":"80%","font_size":"large","color":"#ffffff","align":"center","valign":"top","padding":2}'
```

## Example: a flashing ERROR banner

Flashes red with white text and white with red text five times, then
clears back to black.

```bash
for i in $(seq 1 5); do
  curl -s http://$IP/background -d '{"color":"#ff0000"}'
  curl -s http://$IP/text -d '{"text":"ERROR!","font_size":"large","color":"#ffffff","align":"center","valign":"center"}'
  sleep 0.3
  curl -s http://$IP/background -d '{"color":"#ffffff"}'
  curl -s http://$IP/text -d '{"text":"ERROR!","font_size":"large","color":"#ff0000","align":"center","valign":"center"}'
  sleep 0.3
done
curl -s http://$IP/background -d '{"color":"#000000"}'
```
