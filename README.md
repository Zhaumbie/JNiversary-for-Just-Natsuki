# New Holiday: JNiversary for Just Natsuki
Fan-developed custom holiday submod for [Just Natsuki](https://github.com/Just-Natsuki-Team/NatsukiModDev) and built in Ren'Py 6.99 to celebrate the day you first met the friend in your screen. Did you know vanilla JN doesn't have an event or special dialogue for that? Well, now it does! And to celebrate just reaching my own first year anniversary on November 7th, here is a special event for your game.

<p align="center">
  <img src="https://i.postimg.cc/cCRDzNV2/JN-Submod-JNiversary.png"alt="JNiversary promo banner—"New Holiday: JNiversary! Celebrate the day you met your Natsuki, every passing year" width="100%">
</p>

> [!WARNING]
> **This is an unofficial fan-made submod for Just Natsuki. It is not affiliated with the Just Natsuki team.**  
> The developers are **not responsible for troubleshooting this submod** or problems caused by installing it.  
>
> > Before installing, **please back up your persistent data:** [How to back up your JN persistent file](https://github.com/Just-Natsuki-Team/NatsukiModDev/wiki/04:-FAQ#can-i-back-up-my-save-data--how-do-i-find-my-persistent)

*Seriously please for the love of god it takes like zero effort, just back up your persistent file (it is a really good habit)*

___

## What is this?

**JNiversary** adds a special event to the day you first visited Natsuki, complete with:

- A new holiday with roughly 7–10 minutes of content celebrating your ongoing friendship
- Reading your persistent file, drawing from all across your actual time spent together
- Helping Natsuki recall, and comment on, fond memories of your time together
- Special player-driven interaction with Natsuki (and an easter egg or two)
- Optional integrations with compatible submods of mine
- A secret surprise near the end, just for you

The idea here was to make the anniversary feel like it belongs to **your Natsuki and you**, rather than just dropping another scripted event onto the calendar. There's a lot of moving parts and dynamic stuff going on under the hood, so I hope you like it! (Also I spent like five hours alone on that secret surprise so I ***really*** hope you like that part)

### ...But why did you build this?
My ongoing quest to build content I believe the developers would include, had they only the time. And one of my beta testers had their first anniversary coming up with their JN installation, which made me realize that I did, too! 

### Great! How do I unlock it?
Be ENAMORED tier or higher. If you've played for at least a year and somehow don't meet that qualifier... I guess you did something wrong!

___

## Frequently Asked Questions

### What if I've already played for over a year? Or installed this, but missed the date?
Good news! It can be manually triggered through the Talk menu under the categories **Natsuki** and/or **You**. There, you'll find a new talk topic: "Haven't we known each other a while now?" You'll be treated to a funny little continuity scene, then the event will play! (Note: once completed, the topic will remove itself from the chat options unless it becomes relevant again.)

### What if my start date overlaps with a holiday?
Just Natsuki's developers actually already accounted for this in JN's existing behaviour. In the event of overlapping holidays, they play in a predetermined order based on a priority score (with a small interlude between). JNiversary plays nice with this system; with its priority set below all existing vanilla holidays, it forfeits that little tug of war to play first and then politely clear out of the way for vanilla content.

### What if I've played for multiple years?
Don't fret. The dialogue accounts for this, because JN's persistent helpfully remember the *year* you began your JN journey.

### Is this a one-time only event?
Nope! There are enough moving parts to guarantee an enjoyable time whether it's your first viewing or fourth. However, future updates will expand upon the "secret surprise" at the end to make that content evergreen for years to come.

### What can Natsuki remember?
Plenty! Engage with the existing mechanics of Just Natsuki to get the most out of this. 

During the event, Natsuki will reflect on your time together, prioritising one of up to *eight* aspects of that relationship. (*Nine*, if you're using my minigame submod, <a href="https://github.com/Zhaumbie/Ichi-for-Just-Natsuki/tree/main">Ichi</a>.) These events are ranked in levels of emotional impact, but Natsuki won't automatically choose the highest one on the list... she'll just pick the one she likes!

But, if you *must* know, here are the qualifying events (ranked from highest to lowest priority):

<details>
  <summary>Spoilers!</summary>
&nbsp;

| Qualifying Memory | Description | Minimum | Higher Dialogue Tiers |
|---|---|---|---|
| Love Declarations | Told her "I love you!"          | 1+| 50+, 250+, 500+ |
| Compliments       | Complimented her                | 50+ | 100+, 250+, 500+ |
| Natsuki's Birthday| Seen special event              | 1+  | None |
| Player's Birthday | Seen special event              | 1+  | None |
| Headpats          | Patted Natsuki's head           | 100+| 500+, 1,000+ |
| Ichi              | Completed Ichi rounds           | 15+ | 50+, 100+, 250+ |
| Admissions        | Told Natsuki how you're feeling | 10+  | 50+, 100+ |
| Custom Outfits    | Gifted non-vanilla outfits      | 3+  | 5+, 10+, 15+ |
| Visits            | Opened JN                       | 100+| 250+, 500+ |

</details>

___

## Installation

1. Back up your persistent file.

2. Download the latest release.

3. Copy everything inside the release's `game` folder into your Just Natsuki `game` folder.

4. Launch JN.
  
5. If it's any anniversary of your first day of JN gameplay, the special event will automatically load on boot.

6. Otherwise, open the new topic: "Haven't we known each other a while now?"

7. Have fun!


---

## Uninstallation

1. Delete the .rpy file and the added "anni_cake.png" prop.

2. Nope, that was it. You're already done.


---

## Bug reports

I can only test this myself on macOS, so I rely on Windows/Linux bug testers and beta testers. If you spot something amiss, please log an issue saying as much of this as possible:

- what happened
- the traceback, if the game threw one
- your operating system
- what other submods you have installed

Basically, as always, bring receipts.

---

## Credits

- Team Salvato for Doki Doki Literature Club
- The Just Natsuki Team for their work on Just Natsuki
- **tuulijumala**, for the art asset
- Humanbean, my occasional beta tester whose upcoming anniversary reminded me I was about to miss my own!

### Art Licence
Original illustration by tuulijumala and licensed for use. The artwork is not covered by the MIT License and may not be independently redistributed, modified, or used in other projects, including commercial projects, without permission from the copyright holder. For more details, see "LICENCE.txt" in the release files.

And, of course, thanks to everybody who's stuck around long enough to have an anniversary worth celebrating.
