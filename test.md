## Test table

| Name  | Age | Unrecognized table |
|-------|-----|--------------------|
| Alice | 25  |                    |       
| Bob   | 30  |                    |


| Button             | Function                                           |
|--------------------|----------------------------------------------------|
| 1                  | not supported, no br                               |
| 2 <br>             | supported, has br. will be updated with image link |
| 3 <br> ![](./poop) | supported, has br, has image link                  |
 4 <br> ![](./poop) | supported, malformed table
| 5 <br/> ![](./poop) | supported, <br/> has trailing slash          |
| SHIFT + 6 <i>cool</i> | not supported, wrong html, ![](./poop) is in wrong section          |
| ZORK               | not supported, not recognized button               |

| Button                  | Function                                |
|-------------------------|-----------------------------------------|
| 1 + 2 + 3 <br>          | supported                               |
| 9 + 10 + 11 <br>        | not supported. not recognized buttons.  |
| SYSTEM + Turn dial <br> | supported. case-insensitive internally. |

## BASIC SHORTCUTS

Button | Function
:------------: | -------------
LOOPER PLAY + [1-5] <br> ![a](./manual_images/but/lplay_1..5.png) | Select Scene
REC + [1-3, 7,8] <br> ![b](./manual_images/but/lr_1..378.png) | Select looper sample recording track. A,B,C are mono tracks. Press 7, 8 for stereo recording. 7=A(Left)+B(Right), 8 = B+C. When you do stereo recording, you may want to set pan to left and right for the selected stereo tracks. 
PARAM + [1-3] <br> ![](./manual_images/but/param_1..3.png) | Mute track
MODE PLAY (RECALL) + [1-8] <br> ![](./manual_images/but/mplay_1..8.png) | Recall preset bucket. See the [Preset Bucket](#preset-bucket) section for details.
SEQ PLAY + [1-8] <br> ![](./manual_images/but/mplay_1..8_d.png) | Select Sequencer pattern
SHIFT + LOOPER PLAY + [1-3] button <br> ![](./manual_images/but/s_lplay_1..3.png) | Import WAV file from import folder to selected track
SYSTEM + [1-8] <br> ![](./manual_images/but/sys_1..8.png) | Temporary piano mode

