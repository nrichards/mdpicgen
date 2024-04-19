## Test table

| Name       | Age | Unrecognized table                        |
|------------|-----|-------------------------------------------|
| SHIFT <br> | 25  | not supported, table <br> <br/> no        |       
| 1 <br>     | 30  | not supported, table ![](./poop) <br/> no |


| Button             | Function                                                   |
|--------------------|------------------------------------------------------------|
| 1                  | not supported, no br                                       |
| 2 <br>             | supported, has br. will be updated with image link         |
| 2 <br>             | supported ![](./poop). will be updated with image link     |
| 3 <br> ![](./poop) | supported, has br, has image link                          |
 4 <br> ![](./poop) | supported, malformed table                                 
| 5 <br/> ![](./poop) | supported, <br/> has trailing slash                        |
| SHIFT + 6 <i>cool</i> | not supported, wrong html, ![](./poop) is in wrong section |
| ZORK               | not supported, not recognized button                       |

|              Button               | Description |
|:---------------------------------:|-------------|
| SHIFT + SEQ PLAY + turn dial <br> | Do thing    |


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
| SEQ PLAY + [1-8] <br> ![](./manual_images/but/mplay_1..8_d.png) | Select Sequencer pattern |
| SHIFT + LOOPER PLAY + [1-3] button <br> ![](./manual_images/but/s_lplay_1..3.png) | Import WAV file from import folder to selected track |
SYSTEM + [1-8] <br> ![](./manual_images/but/sys_1..8.png) | Temporary piano mode
B[1-8] (Long press), then PARAM<br> ![](./manual_images/but/1..8_param.png) | Selects a step to lock a parameter for, when in a supported Sequencer sub-mode. See below for more detail.<br><br>(Long press PARAM, also) Clear lock for selected step, or multiple selected steps, if already set.
SEQ PLAY + B[1-8] (Primary pattern) + B[1-8] (2nd pattern) in any sub-mode <br> ![](manual_images/but/splay_1234567812345678.png) | This is a shortcut to select parallel pattern select. <br> * If you press another button while you keep pressing the primary pattern button, then it will be for the 3rd pattern.<br> * If you release the primary pattern button, it will become **Pattern chaining**. <br> * Assign the same pattern one more time to erase the assignment. <br> * Only normal parallel pattern ("R0") can be selected. 

Button | Function
:------------: | -------------
B[1-8] <br> ![](manual_images/but/12345678.png) | Toggle monitor page 
SHIFT + NO <br> ![](manual_images/but/s_n.png) | Toggle between Monitor mode and Mixer
SHIFT + turn dial clockwise almost to end <br> ![](manual_images/but/s_d.png) | Enter the monitor mode. <br>_Tip: SHIFT + turn dial changes sub-mode._
