# =============================================================================
# JNIVERSARY for JUST NATSUKI
# =============================================================================
# Release Version: v1
# =============================================================================
# File: game/submods/Custom Holiday - Jniversary_v1.rpy
# File: game/mod_assets/props/meals/anni_cake.png

# TL;DR // SUMMARY 
# =============================================================================
# Celebrating the anniversary of the day Natsuki met the player!

# =============================================================================
# TABLE OF CONTENTS
# =============================================================================
# 00. Buttons
# 01. Registration
# 02. Topic
# 03. Greeting
# 04. Memories
# 05. Finale
# 06. Spoilers
# 07. Bonus: Ichi
# =============================================================================

default persistent.zhaumbies_custom_events = None
image prop anniversary cake = "mod_assets/props/meals/anni_cake.png"

# "Birthday cake with candles isolated on white background vector"
# Original illustration by tuulijumala. Licensed for use.
# All rights belong to the artist.

# =============================================================================
# 00. BUTTONS – JNIVERSARY CHOICE BUTTON WIDTH OVERRIDE
# =============================================================================
# Uses a dedicated choice screen for the anniversary memory menu only.
# Preserve JN's normal menus, dialogue behavior, choice handling, etc.

init 10 python:
    def jn_anniversary_memory_menu(items, **kwargs):
        # Restore JN's normal menu handler before displaying choices.
        original = renpy.store.jn_anniversary_original_menu
        renpy.store.menu = original

        # Directs this particular menu to the anniversary screen.
        kwargs["screen"] = "jn_anniversary_memory_choice"
        return original(items, **kwargs)

# Sorry, Blizz. But that 50%ish text word-wrap on the buttons is a real pain.
# Please find it in your heart to forgive me
init 10 style jn_anniversary_wide_button is choice_button:
    xsize gui.choice_button_width
    left_padding int(gui.choice_button_width * 0.05)
    right_padding int(gui.choice_button_width * 0.05)

init 10 style jn_anniversary_wide_button_text is choice_button_text:
    xalign 0.5
    text_align 0.5

# Adds a scrollbar to handle all the player choices at the appropriate time.
screen jn_anniversary_memory_choice(items):
    zorder 30
    style_prefix "choice"

    fixed:
        area (690, 30, 485, 480)

        viewport:
            id "jn_anniversary_choices"
            xpos 25
            xsize 450
            ysize 480
            mousewheel True
            draggable True
            arrowkeys True

            vbox:
                style "vbox"
                xalign 0.5
                spacing gui.choice_spacing

                for i in items:
                    textbutton i.caption:
                        style "jn_anniversary_wide_button"
                        text_style "jn_anniversary_wide_button_text"
                        action i.action
                        hover_sound gui.hover_sound
                        activate_sound gui.activate_sound

        bar:
            style "classroom_vscrollbar"
            value YScrollValue("jn_anniversary_choices")
            xalign scroll_align
            ysize 480


# =============================================================================
# 01. REGISTRATION & HOLIDAY SELECTION
# =============================================================================

init 2 python in jn_anniversary:
    import calendar
    import datetime
    import store
    import store.jn_events as jn_events
    import store.jn_affinity as jn_affinity

    # Any custom holidays I write can be installed independently. Only create this
    # shared dictionary when it's missing. We'll leave everybody else's keys alone.
    if store.persistent.zhaumbies_custom_events is None:
        store.persistent.zhaumbies_custom_events = {}
    if isinstance(store.persistent.zhaumbies_custom_events, dict):
        record = store.persistent.zhaumbies_custom_events.setdefault("jn_anniversary", {})
        if isinstance(record, dict):
            record.setdefault("last_completed_year", 0)
        del record

    def completed_year():
        holidays = store.persistent.zhaumbies_custom_events
        record = holidays.get("jn_anniversary") if isinstance(holidays, dict) else None
        year = record.get("last_completed_year") if isinstance(record, dict) else None
        if type(year) in (int, long) and year >= 0:
            return year
        return None

    # Protect player progress even if another submod writes an unexpected value.
    if completed_year() is None:
        store.jn_utils.log(
            "JNiversary unavailable: expected a nonnegative last_completed_year in zhaumbies_custom_events.",
            store.jn_utils.SEVERITY_ERR
        )

    # Vanilla's enum has ten fixed members. This attribute is an integer, not an
    # eleventh enum member. The holiday filter compares tokens and complete() stores
    # int(token). We'll keep this ID stable obviously.
    TYPE = 0x4A4E01
    if any(int(member) == TYPE for member in jn_events.JNHolidayTypes):
        raise ValueError("Oops! JNiversary holiday ID already belongs to a vanilla holiday.")

    def milestone(day):
        first = store.persistent.jn_first_visited_date
        if not isinstance(first, datetime.date):
            return 0, None

        # Standard JN procedure: February 29 players celebrate on February 28.
        years = day.year - first.year
        while years > 0:
            year = first.year + years
            due = datetime.date(year, first.month, min(first.day, calendar.monthrange(year, first.month)[1]))
            if due <= day:
                return years, due
            years -= 1

        return 0, None

    # Both registrars are private. Ask Ren'Py for their names using the defining
    # functions' own filenames. JN's registrars also load saved data.
    if getattr(jn_events.JNHolidayTypes, "jn_anniversary", TYPE) != TYPE:
        raise ValueError("JNiversary holiday name already in use.")
    if any(int(other.holiday_type) == TYPE for other in jn_events.getAllHolidays()):
        raise ValueError("JNiversary holiday ID already in use.")
    jn_events.JNHolidayTypes.jn_anniversary = TYPE

    register_holiday = getattr(jn_events, renpy.munge("__registerHoliday", jn_events.getHoliday.func_code.co_filename))
    register_holiday(jn_events.JNHoliday(
        label="holiday_jn_anniversary",
        holiday_type=jn_events.JNHolidayTypes.jn_anniversary,
        affinity_range=(jn_affinity.ENAMORED, None),
        natsuki_sprite_code="1nchgnlsbr",
        deco_list=["balloons"],
        prop_list=[],
        priority=5,
        # I set priority as "5" to ALWAYS go first before overlapping holidays ("10").
        conditional="jn_anniversary.pending(datetime.date.today())[0] > 0"
    ))

    def pending(day):
        year, due = milestone(day)
        finished = completed_year()
        if finished is not None and year > finished:
            return year, due
        return 0, None

    # Both the holiday selector and the Talk script ask this calendar about dates. 
    # We add our anniversary date here, before JN filters for affinity, seen state,
    # completion, etc. This also preserves dates supplied by an earlier extension.
    previous_calendar = jn_events.getHolidaysForDate

    def holidays_for_date(input_date=None):
        if input_date is None:
            input_date = datetime.datetime.today()
        found = previous_calendar(input_date)
        day = input_date
        if isinstance(day, datetime.datetime):
            day = day.date()
        year, due = milestone(day)
        if year and due == day and TYPE not in found:
            return list(found) + [TYPE]
        return found

    jn_events.getHolidaysForDate = holidays_for_date

    def years_phrase(year):
        # I'll have to write 4–5 different anniversary scripts another time.
        # For now, we'll keep Natsuki commenting specifically on the number of years in
        # a dynamic way. You guessed it: substitution!
        names = {1: "a", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}
        if year == 1:
            return "a whole year"
            # "one whole year" reads clunky af to my eyes/ears
        return "{0} whole years".format(names.get(year, str(year)))

    def valid_milestone(year):
        finished = completed_year()
        return (type(year) in (int, long) and finished is not None
                and finished < year <= milestone(datetime.date.today())[0])

    def finish(year, page, late=False):
        # One uninterrupted Python statement at the end of the scene. No interaction or
        # disk write between unlocking the poem and the party.
        if not valid_milestone(year):
            return
        if page is not None:
            page.unlock()
        holiday = jn_events.getHoliday("holiday_jn_anniversary")
        holiday.complete()
        # Belated parties keep their balloons for this session, not future visits.
        if late:
            store.persistent._jn_holiday_deco_list_on_quit = []
        store.persistent.zhaumbies_custom_events["jn_anniversary"]["last_completed_year"] = year

        # A late party can use this year's annual flag before the next milestone falls 
        # due. In that case? Release just our two annual flags. This keeps JN's shown
        # count, session decorations, general persistent, and other holidays intact.
        if store.persistent.jn_first_visited_date.year + year + 1 <= datetime.date.today().year:
            holiday.is_seen = False
            store.persistent._jn_holiday_list[holiday.label] = holiday.asDict()
            if TYPE in store.persistent._jn_holiday_completed_list:
                store.persistent._jn_holiday_completed_list.remove(TYPE)

        # NMA compatibility: permanently remember each celebrated anniversary.
        # NMA is optional. JNiversary works normally without it.
        kcs = getattr(store, "jn_kcs", None)

        if kcs is not None and hasattr(kcs, "record_external_event"):
            anniversary_due = milestone(datetime.date.today())[1]

            try:
                kcs.record_external_event(
                    source="jniversary",
                    event_type="anniversary_celebrated",
                    data={
                        "milestone_id": "year_{0}".format(year),
                        "anniversary_year": year,
                        "anniversary_due_date": anniversary_due.isoformat(),
                        "celebrated_late": anniversary_due < datetime.date.today()
                    },
                    importance=3
                )

            except Exception as exception:
                store.jn_utils.log(
                    "Logging 'No More Amensia' milestone for 'JNiversary' failed: {0}".format(exception),
                    store.jn_utils.SEVERITY_ERR
                )

        renpy.save_persistent()


    def missed():
        today = datetime.date.today()
        year, due = pending(today)
        return bool(year and due < today and store.Natsuki.isEnamored(higher=True))

    # Weighted lottery for the memories Natsuki brings up herself.
    # Didn't want to just randomize this——some should be more impactful than others!
    # Bigger number means greater emotional weight, but lower can still be picked.
    # This lets me enable Natsuki's decisions without forcing her decisions.
    MEMORY_PRIORITIES = {
        "love": 10,
        "compliments": 8,
        "natsuki_birthday": 6,
        "player_birthday": 6,
        "headpats": 5,
        "ichi": 5,          # Only relevant if Ichi is installed. See below.
        "admissions": 4,
        "outfits": 4,
        "visits": 3,
    }

    def ichi_results():
        # Ichi's optional. On builds without it, we obviously ignore it. A completed
        # quickplay game counts as one round; each Advanced round counts separately,
        # even within an unfinished match.
        if not hasattr(store, "jn_ichi") or not renpy.has_label("talk_play_ichi"):
            return None

        # A quick check: is Ichi is even HERE on this build?
        memory = getattr(store.persistent, "_jn_ichi_memory", None)
        if not isinstance(memory, dict):
            return None

        # Fields gleaned from the Ichi submod.
        keys = (
            "quickplay_player_wins",
            "quickplay_natsuki_wins",
            "advanced_player_round_wins",
            "advanced_natsuki_round_wins"
        )
        values = []
        for key in keys:
            value = memory.get(key, 0)
            if type(value) not in (int, long) or value < 0:
                return None
            values.append(value)

        # Basic calculations for win/lose values for both players.
        player_wins = values[0] + values[2]
        natsuki_wins = values[1] + values[3]
        total_rounds = player_wins + natsuki_wins
        if total_rounds < 15:
            return None

        # This checks to see if either one has a 30-percentage-point Ichi victory lead.
        # That value lets us get a liiiiittle more creative with Natsuki's dialogue.
        if (player_wins - natsuki_wins) * 100 >= total_rounds * 30:
            leader = "player"
        elif (natsuki_wins - player_wins) * 100 >= total_rounds * 30:
            leader = "natsuki"
        else:
            leader = "close"

        return (total_rounds, player_wins, natsuki_wins, leader)

    def choose_memory(available):
        if not available:
            return None
        total = sum(MEMORY_PRIORITIES[name] ** 2 for name in available)
        ticket = renpy.random.randint(1, total)
        for name in available:
            ticket -= MEMORY_PRIORITIES[name] ** 2
            if ticket <= 0:
                return name
        return available[-1]

    # Future-proofing for PGC, which keeps event decorations in the classroom.
    def needs_classroom():
        if hasattr(store, "jn_pgc") and hasattr(store.jn_pgc, "currentLocation"):
            return store.jn_pgc.currentLocation() != "classroom"

        # Don't assume a future location manager exists in vanilla JN.
        background = getattr(store, "main_background", None)
        location = getattr(background, "location", None)
        return getattr(location, "id", "classroom") != "classroom"

    # If in a custom location... nope! Gotta go back to the classroom first!
    def go_to_classroom():
        if not needs_classroom():
            return True

        if not hasattr(store, "jn_pgc") or not hasattr(store.jn_pgc, "moveTo"):
            return False

        # If an enforced location change fail, let's postpone the celebration.
        try:
            return bool(store.jn_pgc.moveTo("classroom", covered=True))

        except Exception as exception:
            store.jn_utils.log(
                "JNiversary couldn't return to the classroom: {0}".format(exception),
                store.jn_utils.SEVERITY_ERR
            )
            return False


# =============================================================================
# 02. TOPIC (MISSED ANNIVERSARY)
# =============================================================================
# This system allows the player to invoke a missed anniversary event——whether
# by accident or just not having this submod installed prior to 365 days of JN.
# The automatic holiday and the missed-date Talk topic share a greeting.

init 5 python:
    registerTopic(
        Topic(
            persistent._topic_database,
            label="talk_jn_anniversary",
            prompt="Haven't we known each other a while now?",
            category=["Natsuki", "You"],
            unlocked=True,
            player_says=True,
            conditional="jn_anniversary.missed()",
            affinity_range=(jn_affinity.ENAMORED, None),
            location="classroom"
        ),
        topic_group=TOPIC_TYPE_NORMAL
    )

label talk_jn_anniversary:
    $ anniversary_year, anniversary_due = jn_anniversary.pending(datetime.date.today())
    if not anniversary_year or not jn_anniversary.missed():
        return

    n 6tchbgsbl "I mean, yeah!{w=0.5}{nw}"
    extend 6ctlbs " Obviously!"
    $ anniversary_month = persistent.jn_first_visited_date.strftime("%B")
    n 7tllaj "We met back in [anniversary_month],{w=0.5}{nw}"
    extend 7tdlaj " and...{w=0.3}{nw}"
    extend 7kdwaj "{w=1}{nw}"
    extend 4cskajsbr " wait...{w=0.75}{nw}"
    extend 1uskemsbr " {i}no.{/i}"
    n 3fbkgslsbr "NO!"
    n 3fsgwrlsbr "[player], we missed the anniversary of the day we met!"
    n 4fcsflsbr "Oh my god!{w=0.5}{nw}"
    extend 4fdtgtfsbr " Are you {i}kidding{/i} me?!"
    n 4cslpulsbr "Tch.{w=0.3}{nw}"
    extend 1fcsajlsbr " Okay!{w=0.5}{nw}"
    extend 4cslsslsbl " You know what...?{w=0.3}{nw}"
    extend 1csqsrlsbr " Doesn't matter!"
    n 2ksqbslsbr "Who says we can't celebrate it now?"
    n 4fchgnlsbr "And we're {i}going{/i} to! I've got plans!"

    if jn_anniversary.needs_classroom():
        n 4tllaj "...Wait, I've got some stuff put away in the classroom closet."
        n 2fsqssl "And no, you're not getting any hints about what it is!"
        n 4fchbg "Just give me a few to get something ready, okay?"

    else:
        n 7ctldvlsbr "I just need a moment to grab something."
        n 2fsqsslsbr "And don't even {i}think{/i} about peeking!"

    n 6nwmsgfsbr "You stay right there, [player]!{w=0.75}{nw}"
    extend 6nchgnf " I'll be right back!"

    # Annnnd now we pass everything over to the anniversary celebration greeting.
    call holiday_jn_anniversary(anniversary_year, True) from talk_jn_anniversary_return
    return


# =============================================================================
# 03. GREETING: MAIN ANNIVERSARY CONTENT
# =============================================================================
# The count is a quick early beat. Everything after it is the same story.
# We keep JN's holiday object, plus its visuals and its progression machinery.

label holiday_jn_anniversary(anniversary_year=jn_anniversary.milestone(datetime.date.today())[0], late=False):
    if (
        not Natsuki.isEnamored(higher=True)
        or type(anniversary_year) not in (int, long)
        or anniversary_year < 1
        or anniversary_year != jn_anniversary.pending(datetime.date.today())[0]
    ):
        return

    # The holiday is kept in the classroom until future location support is ready.
    # PGC remains optional; nothing here mentions an unreleased feature to Nat.
    if jn_anniversary.needs_classroom():

        show black zorder JN_BLACK_ZORDER with Dissolve(0.6)
        $ jnPause(0.4)
        $ anniversary_relocated = jn_anniversary.go_to_classroom()
        if not anniversary_relocated:
            hide black with Dissolve(0.5)
            n 4cslsrl "Ugh...{w=0.5} Something went wrong. I can't get everything set up right now."
            n 2kdwssl "Could we try this again later...?{w=0.5}{nw}"
            extend 4kwmbgl " This really matters to me."
            return
        $ jnPause(0.4)


    elif late:
        show black zorder JN_BLACK_ZORDER with Dissolve(0.5)

    # A more natural transition from the talk topic jumping straight into the event.
    if late:
        stop music fadeout 2.0        
        play audio chair_out
        $ jnPause(1.0)
        n 4nllaj "First things first...{w=2}{nw}"
        play audio drawer
        $ jnPause(1.15)
        n 4uskaj "Huh? Where did I...?{w=2}{nw}"
        play audio drawer
        $ jnPause(1.0)
        n 2fcsfl "Oh, come on! Weren't those right here...?{w=2}{nw}"
        play audio clothing_ruffle
        $ jnPause(0.9)
        n 1nchbg "Aha! There you are!{w=2}{nw}"
        play audio drawer
        $ jnPause(0.9)
        n 4kslss "Just a little bit...{w=2}{nw}"
        play audio chair_in
        $ jnPause(1.25)
        n 2fchbg "All right! All done!{w=2}{nw}"
        $ jnPause(1)

    # Save the current desk item so it can be restored afterward.
    # Spoiler alert, it's the anniversary cake.
    $ anniversary_previous_desk_centre = Natsuki._desk_centre[:]

    # Draw the cake as part of Natsuki's sprite and desk.
    # This makes it follow her automatically during choice menus.
    # God this was so irritating to figure out like ten months ago.
    $ Natsuki.setDeskItem(
        "mod_assets/props/meals/anni_cake.png",
        jn_desk_items.JNDeskSlots.centre
    )
    # Believe it or not, making the desk prop move when a choice menu came up was my
    # biggest early hurdle with JN submodding. HATED that Wintendo Twitch! Haha.
    # Anyway, let's get back to the useful comments again.

    # Reveal Natsuki, the cake, decorations, and anniversary music.
    $ jn_events.getHoliday("holiday_jn_anniversary").run()

    # Generate the natural year wording once, with a version for shouting.
    $ anniversary_year_phrase = jn_anniversary.years_phrase(anniversary_year)
    $ anniversary_year_phrase_upper = anniversary_year_phrase.upper()
    $ player_upper = player.upper()
    $ n_name_upper = n_name.upper()

    if late:
        n 1nchbgl "TA-DAAAA!"

        show natsuki 4fspbsl at jn_left
        menu:
            n "HAPPY BELATED ANNIVERSARY, [player_upper]!"

            "Happy belated anniversary, [n_name]!":
                show natsuki 4fchbgl at jn_center
                pass

            "HAPPY BELATED ANNIVERSARY, [n_name_upper]!":
                show natsuki 2nchbsfelg at jn_center
                n "Look who's getting in the spirit, too!"

        n 4fchbgl "WE MET OVER [anniversary_year_phrase_upper] AGO!"
        n 1clrbgl "{i}So what{/i}{w=0.25} if we missed the exact day?{w=0.5}{nw}"
        extend 2ccssrl " Who says we've gotta pretend it never happened?"
        n 2fsqsmlsbr "Just means we can celebrate it{w=0.3} {i}right now.{/i}"
        n 2fsrssl "And if you think I was gonna ignore something this important without making a fuss..."
        n 2ctrbgl "Then{w=0.2} {i}obviously{/i}{w=0.3} you need to spend more time with me.{w=0.5}{nw}"
        extend 2cchlglelg " Ahaha!"

    else:
        n 1nchlgl "YAAAAAY!"

        show natsuki 4nspbsl at jn_left
        menu:
            n "HAPPY ANNIVERSARY, [player_upper]!"

            "Happy anniversary, [n_name]!":
                show natsuki 4fchbgl at jn_center
                pass

            "HAPPY ANNIVERSARY, [n_name_upper]!":
                show natsuki 2nchbsfelg at jn_center
                n "Look who's getting in the spirit, too!"

        n 4fchbgl "WE MET [anniversary_year_phrase_upper] AGO TODAY!"
        n 2fsqbg "Yeah! You heard me!"
        n 1nchgn "Come on!{w=0.3} Tell me that's not worth making a huge fuss over!"
        n 4fchbgl "I mean, look at all this!{w=0.5}{nw}"
        extend 4tdwsgl " I even made us a cake!"

    n 6ncsbslsbr "Okay, okay...{w=0.75}{nw}"
    extend 2tchbgl " {i}maybe{/i} I'm getting a little carried away."
    n 4kslsslsbr "I just...{w=0.75}{nw}"
    extend 4ksqsglsbr " really wanted it to be a special occasion, you know?"
    n 1kwmssl "It's not every day I get to celebrate something this important with my favorite person."
    n 2fsqsslsbr "You're just gonna have to put up with me being excited!"
    $ anniversary_month = persistent.jn_first_visited_date.strftime("%B")
    n 1ncssml "So...{w=0.75}{nw}"
    extend 1twmajl " do you still remember when you first showed up here?{w=1}{nw}"
    extend 4kslsslsbr " Back in [anniversary_month]?"
    n 4kwmssl "We've known each other for [anniversary_year_phrase], [player]."

    if late:
        pass

    else:
        n 1uskssfsbl "And it's today!{w=0.3}{nw}"
        extend 4kdrssl " The anniversary of the day we met."
        n 4ksrssl "I kept checking the calendar like it might change if I looked away."

    n 2fcsajl "Obviously, I didn't know what to expect from you back then."
    n 4tsqpul "And don't pretend {i}you{/i} knew what you were getting into, either!"
    n 4kllbol "We really {i}were{/i} complete strangers back then, weren't we...?{w=1.25}{nw}"
    extend 5fsqbslsbr " So I definitely made you work for it."
    n 5ncssml "I've got standards.{w=0.5}{nw}"
    extend 5nkrssl " And you stuck around, so...{w=1}{nw}"
    extend 5nsrbgl " clearly you do, too."
    n 1nchsglsbr "Well, good news.{w=0.3}{nw}"
    extend 5nkrsgfsbr " It really paid off."
    n 5twmbglsbr "So I wanted to do something special for you...{w=0.5}{nw}"
    extend 5cdrfllsbr " though I kept worrying it'd be dumb."
    n 2fsqajsbl "Which is{w=0.2}{nw}"
    extend 2fcsflsbl " {i}stupid.{/i}{w=0.75}{nw}"
    extend 2ftlfrsbl " Obviously."
    n 4cslsslsbr "I really should know by now you're the {i}last{/i} person I should be worrying about that with."
    n 4kllsslsbr "I guess I just...{w=0.75}{nw}"
    extend 4kwmsrlsbr " I cared a lot about getting this right."
    n 1nchsml "So...{w=0.3}{nw}"
    extend 2fchbgl " {i}happy anniversary, [player]{/i}!"

    # Exact project-native confetti choreography, also used on her birthday.
    play audio smack
    show confetti falling at jn_confetti_fall zorder JN_PROP_ZORDER
    $ jnPause(1.25)
    n 2fchbslsbr "Aha!{w=0.25} Bet you weren't expecting that!"
    hide confetti
    show confetti desk zorder JN_PROP_ZORDER

    n 1cslsgl "...Okay, maybe you were.{w=0.5}{nw}"
    extend 2fsqsslsbr " It's not like I tried to hide the cake."
    n 2fchgnl "But you've gotta admit it looks pretty good!"

    if Natsuki.isLove(higher=True):
        n 5ksqsmf "What?{w=0.25} Your girlfriend's allowed to get excited about the day we met!"
        n 5fsrsmfsbl "Actually, I'm pretty sure it's in the rules somewhere."

        show natsuki 5kwmsmfsbl at jn_left
        menu:
            n  "I love you, [player].{w=0.5} I just really wanted us to have this."

            # The golden path, where life is joy
            "I love you too, [n_name]!":
                show natsuki 4nchbgf at jn_center
                n "Oh, I know you do."
                n 4nwmbgfsbr "You're always proving it to me...{w=0.3}{nw}"
                extend 4nsqbsfsbr " you big softie."

            # God help you
            "(Choose to not say it back, and thus be held liable for your crimes.)":
                show natsuki 4nchbgf at jn_center
                n "...{w=1}{nw}"
                extend 4nskbgf "I'm sorry?"

                # Uh-oh
                play audio kettle_boil
                $ jnPause(2)

                # Someone done did it now
                n 4nchbgf "Ehehe."
                n 4nscunfsbr "I think you{w=0.3}{nw}"
                extend 4fscfrfsbr " {i}forgot something,{/i} dummy..."

                show natsuki 2fscgsf at jn_left
                menu:
                    n "So are we {i}gonna have a problem{/i}, or...?"

                    "Just kidding! I love you too, [n_name].":
                        show natsuki 2fsrsrf at jn_center
                        n "Hmph.{w=1}{nw}"
                        extend 2csqsrf " I should definitely dock you points for that one."
                        n 2fslssfsbr "You're lucky you're cute..."

    else:
        n 2fcsbgl "It's an anniversary with my best friend!{w=0.5}{nw}"
        extend 4fsqajl " Of course I'm making a fuss!"
        n 5kdwsml "You {i}know{/i} you're a pretty big deal to me..."

    show natsuki 1kwmunlsbl at jn_left
    menu:
        n "S-{w=0.2}so... what do you think?"

        "Meeting you changed my life for the better.":
            $ anniversary_answer = "changed"
            show natsuki 1uskajfsbl at jn_center
            n 1uskajfsbl "W-{w=0.2}what?!"
            n 4fllpofsbr "You can't just say that while I'm trying to keep it together!"
            n 1kslsslsbl "...But I'm really glad I made a difference to you."
            n 1kwmbgf "You've made a pretty big one to me, too."

        "I wouldn't trade what we have for anything.":
            $ anniversary_answer = "glad"
            show natsuki 1ksrsslsbl at jn_center
            $ jnPause(0.75)
            n 4ksrsmfsbr "...Jeez."
            n 4kwmssl "You mean that?{w=0.5}{nw}"
            extend 5kdwsslsbr " I mean,{w=0.3} I know you do.{w=0.5}{nw}"
            extend 5kcssml " I just really like hearing it."
            n 2twmajl "And for the record?{w=0.5}{nw}"
            extend 4ckrbsl " Neither would I."

        "Thank you for trusting me with so much of yourself, [n_name]." if Natsuki.isEnamored(higher=True):
            $ anniversary_answer = "trust"
            show natsuki 4nchgnf at jn_center
            n "Ehehe."
            n 4kslsslsbl "Well, you've been pretty good about listening."
            n 4fcsflsbr "I just...{w=0.5} really wanted this to be good.{w=0.75}{nw}"
            extend 4ccssrfsbr " For you."
            n 1knmsmlsbl "But thanks.{w=0.5}{nw}"
            extend 1kwmsml " Guess I kinda needed to hear that."

        "You're the best girlfriend ever." if Natsuki.isLove(higher=True):
            $ anniversary_answer = "love"
            show natsuki 5uskajfsbl at jn_center
            $ player_initial = jn_utils.getPlayerInitial()
            n 5uskajfsbl "[player_initial]-[player]?!"
            n 5kslssfsbl "...{w=1}{nw}"
            $ chosen_tease = jn_utils.getRandomTease()
            extend 5kwmsmfsbl "W{w=0.1}-well.{w=0.3} I'm glad you feel that way, [chosen_tease]."
            n 5ksqsmf "Because I'm pretty happy being yours."
            n 4fcsflfsbr "I just... really wanted this to be good.{w=0.5}{nw}"
            extend 4ckrsrfsbr " For you."
            n 1kslssf "...{w=0.3}{nw}"
            extend 1knmsmfsbl "But thanks.{w=0.5}{nw}"
            extend 1nchbsfsbl " This {i}was{/i} a lot of work."

    n 4kdwssl "You know what I kept thinking about when I was planning this?"
    n 1utlpul "The simple stuff.{w=0.5}{nw}"
    extend 1kllssl " All the times we just hung out and talked about whatever.{w=1}{nw}"
    extend 1kchbgl " And you'd let me ramble, and go on a tangent..."
    n 7csrpul "A {i}lot{/i} of tangents, come to think of it..."
    n 4cdwssl "Point is, I don't have to sit here wondering if you're judging me for it."
    n 1kcssmf "...Ehehe."
    n 4kslsslsbl "I guess that's kind of a weird thing to be grateful for,{w=0.75}{nw}"
    extend 4ksqsslsbl " isn't it?"
    n 1kdwsrl "But there was a time when I didn't think I could do that with anyone."
    n 4kcsfll "I used to think somebody really knowing me would be...{w=0.75}{nw}"
    extend 4kcsfrl " awful."
    n 2csrssl "Deciding how I was at the drop of a hat.{w=0.75}{nw}"
    extend 2fsrsrl " My hobbies.{w=0.3} What I look like.{w=0.5}{nw}"
    extend 2fsqsrl " That kind of thing."
    n 4fupsml "And yeah, sometimes I {i}was{/i} a pain to deal with.{w=0.75}{nw}"
    extend 4ccsfrl " Nobody's perfect!"

    if Natsuki.isLove(higher=True):
        n 5kslssfsbl "But being in love with somebody who knows me that well?"
        n 5fcsflfsbr "G-{w=0.2}god, saying it out loud sounds so {i}cheesy!{/i}"
        n 2cdwpufsbl "...Ugh."
        n 4kcsssf "But it's true.{w=0.5}{nw}"
        extend 5nslbgf " I{w=0.25} {i}love{/i}{w=0.3} being your girlfriend."
    else:
        n 5kllssl "I get to call you my best friend, [player]."
        n 5fcsajl "And no, I'm not just saying that because it's the anniversary of the day we met."
        n 5kwmsml "I get to be myself around you."
        extend 5nchbgf " And I {w=0.3}{i}love{/i}{w=0.25} that."

    show natsuki 5ksrpufsbl at jn_left
    menu:
        n  "I cherish it so much."

        "Same, [n_name].":
            show natsuki 4kwdgsfeex at jn_center
            n "R-{w=0.1}really...?" 
            n 4kdwbgfsbr "[player]..."
            n 2kcspul "I-{w=0.1}I...{w=0.25} I can't put into words how much that means to me."
            n 2kdrajl "If it's not too much trouble...{w=0.5}{nw}"
            extend 2tdlbol " could I ask..."

    show natsuki 2kcubof at jn_left
    menu:
        n "Can you tell me more...?"

        "The quiet, ordinary moments together matter so much to me.":
            $ anniversary_focus = "quiet"
            show natsuki 1kwmsslsbl at jn_center
            n "Yeah.{w=0.75}{nw}"
            extend 1nchbsf " I really like those, too."
            n 4kchsgl "I don't always feel like I need to have something ready to say."
            n 2twmsmlsbr "Don't worry, though.{w=0.5}{nw}"
            extend 4kslsslsbr " I'm not running out of things to talk about!"
            n 1nchsml "Not even close."

        "I love seeing these sides of you that everyone else missed.":
            $ anniversary_focus = "noticed"
            show natsuki 1uskajfsbl at jn_center
            n 1uskajfsbr "W-{w=0.2}what?!{w=0.25}{nw}"
            extend 2tsrflfsbr " I don't really feel like I'm all that complicated..."
            n 1kllssl "...But that's actually kind of nice."
            n 2tsgbgfsbr "I think I get what you're saying."
            n 1ksrsml "And I like knowing you pay attention to who I really am."

        "We still have so much more to learn about each other.":
            $ anniversary_focus = "future"
            show natsuki 1nchsml at jn_center
            n 3fchgnlsbl "Yeah!{w=0.25} Exactly!"
            n 2fcsbgl "I don't want us to stop being curious just because we're comfortable."
            n 1kwmsslsbr "I wanna hear what you think about things.{w=0.5}{nw}"
            extend 1csrbgl " Even when you're wrong."
            n 2tchbsl "Which, let's be fair, is bound to happen sometimes!"
            n 2fsqsml "Not me though.{w=0.5}{nw}"
            extend 2fsrbglsbr " {i}My{/i} opinions are perfect."
            n 2fsqsml "...{w=1.25}{nw}"
            n 2cchlglelg "Well.{w=0.3} I {i}nearly{/i} got through that with a straight face!"

    # That Vacation song is EXCELLENT... in shorter bursts. By now, it's tiring.
    # We also don't want the stereo prop interfering with the cake. So...

    n 2csrpul "Hmm...{w=1}{nw}"
    extend 2tsqssl " hold that thought."
    n 4nchbgl "I'm gonna change this music.{w=0.5} Just give me a sec, okay?"

    # Blackout. No props are shown or moved.
    show black zorder JN_BLACK_ZORDER with Dissolve(0.6)
    $ jnPause(1)

    # Natsuki hypothetically gets out the stereo and switches the current music.
    play audio button_tap_c
    $ jnPause(0.5)
    play audio gift_close
    $ jnPause(1)
    play audio button_tap_c
    stop music fadeout 1.0
    $ jnPause(1.5)

    # We choose the standard daytime or nighttime classroom music. 
    # Those are classics! And I'll hear NOTHING to the contrary. Nothing!
    $ anniversary_music = "strawberry_daydream.ogg" if main_background.isDay() else "stars_that_shimmer.ogg"

    play audio button_tap_c
    $ renpy.play(
        filename=jn_custom_music.getMusicFileRelativePath(
            file_name=anniversary_music,
            is_custom=False
        ),
        channel="music",
        fadein=1.0
    )
    $ jnPause(0.5)

    # Natsuki hypothetically puts away the stereo.
    play audio gift_close
    $ jnPause(1.0)

    n 2kchbslsbr "Ahh...{w=0.3}{nw}"
    extend 2ksqbglsbr " that's better."
    $ jnPause(1.0)

    # Annnnd we reveal the classroom with the anniversary cake still looking great.
    hide black with Dissolve(0.7)

    n 5csrfllsbr "Now, what was I saying again...?"
    n 5uwdgsleexsbr "Oh!{w=0.5}{nw}"
    extend 5tlrbglsbr " Right..."

    # Oh, right. Back to the memory_choice stuff.
    # The first choice mattered, too. This is her response to what you said.
    if anniversary_answer == "trust":
        n 5tdlsslsbl "Back to what you said a second ago...?{w=0.5}{nw}"
        extend 1nchbglsbr " I'm just glad I don't have to be afraid of trusting you with the real stuff."
    elif anniversary_answer == "love":
        $ chosen_tease = jn_utils.getRandomTeaseName()
        n 5kslssfsbl "I'm still thinking about what you said earlier, you big [chosen_tease]."
        n 5kwmsmf "...Love you."
    elif anniversary_answer == "changed":
        n 4kwmsslsbr "About what you just said about meeting me...?{w=0.75}{nw}"
        extend 5kllbgl " That's a pretty big thing to tell somebody."
        n 5nchbsl "And I'm really happy you did."
    else:
        n 5tdrsslsbl "I guess what I'm trying to say is...{w=0.75}{nw}"
        extend 1kwmsml " I really am glad we found each other, [player]."


# =============================================================================
# 04. MEMORIES: QUALIFYING EVENTS
# =============================================================================
# Only offer memories confirmed by JN or the installed Ichi submod (if present).
# Natsuki gets a weighted choice, and the player gets one she didn't choose.

    $ anniversary_ichi = jn_anniversary.ichi_results()
    $ anniversary_memories = []

    # Count unlocked custom outfits, excluding official JN outfits.
    # Individual clothing pieces don't count as complete outfits.
    python:
        anniversary_outfit_count = len(
            jn_outfits.JNOutfit.filterOutfits(
                outfit_list=jn_outfits.getAllOutfits(),
                unlocked=True,
                is_jn_outfit=False
            )
        )

        # This reads the history of all vanilla admission topics.
        anniversary_admission_counts = dict(
            (topic.label, topic.shown_count)
            for topic in jn_admissions.ADMISSION_MAP.values()
        )
        # JN's persistent counts admissions separately, so we quickly tally them.
        anniversary_admission_count = sum(
            anniversary_admission_counts.values()
        )
        # This identifies the feeling the player has mentioned most often.
        # Ties are resolved consistently by topic label.
        anniversary_admission_focus = None
        anniversary_admission_feeling = None

        if anniversary_admission_count:
            anniversary_admission_focus = max(
                (count, label)
                for label, count in anniversary_admission_counts.items()
            )[1]

            anniversary_admission_feeling = (
                anniversary_admission_focus.replace("admission_", "", 1)
            )

        # Describe Natsuki's custom wardrobe by its current size.
        if anniversary_outfit_count >= 15:
            anniversary_outfit_descriptor = "so many"
        elif anniversary_outfit_count >= 10:
            anniversary_outfit_descriptor = "plenty of"
        elif anniversary_outfit_count >= 5:
            anniversary_outfit_descriptor = "some"
        else:
            anniversary_outfit_descriptor = "a few"

    python:
        # Use the actual most-repeated compliment, not a fixed topic.
        # Wording matches the compliment's meaning in script-compliments.rpy.
        # Ties keep the first entry so the choice is predictable.
        anniversary_compliment_wording = (
            ("compliment_amazing", "amazing"),
            ("compliment_beautiful", "beautiful"),
            ("compliment_confident", "confident"),
            ("compliment_cute", "cute"),
            ("compliment_hilarious", "funny"),
            ("compliment_inspirational", "inspiring"),
            ("compliment_style", "stylish"),
            ("compliment_thoughtful", "thoughtful")
        )
        anniversary_compliment_counts = []
        for topic_label, wording in anniversary_compliment_wording:
            compliment_topic = get_topic(topic_label)
            if compliment_topic is not None:
                anniversary_compliment_counts.append(
                    (compliment_topic.shown_count, wording)
                )
        # JN's persistent counts compliments separately, so we quickly tally them.
        anniversary_compliment_total = sum(
            count for count, wording in anniversary_compliment_counts
        )

        # This identifies the compliment Natsuki has heard most often.
        compliment_descriptor = None
        if anniversary_compliment_total > 0:
            compliment_descriptor = max(
                anniversary_compliment_counts,
                key=lambda item: item[0]
            )[1]

    # Minimum qualifier for Natsuki commenting on love confessions.
    if Natsuki.isLove(higher=True):
        $ anniversary_memories.append("love")

    # Minimum qualifier for Natsuki commenting on compliments.
    if anniversary_compliment_total >= 50:
        $ anniversary_memories.append("compliments")

    # Only remember Natsuki's birthday if it was celebrated.
    if jn_events.getHoliday("holiday_natsuki_birthday").shown_count > 0:
        $ anniversary_memories.append("natsuki_birthday")

    # Only remember the player's birthday if it was celebrated.
    if jn_events.getHoliday("holiday_player_birthday").shown_count > 0:
        $ anniversary_memories.append("player_birthday")

    # Minimum qualifier (helper) for Natsuki commenting on Ichi.
    if anniversary_ichi is not None:
        $ anniversary_memories.append("ichi")

    # Minimum qualifier for Natsuki commenting on headpats.
    if persistent._jn_headpats_total_given >= 100:
        $ anniversary_memories.append("headpats")

    # Minimum qualifier for Natsuki commenting on admissions.
    if anniversary_admission_count >= 10:
        $ anniversary_memories.append("admissions")

    # Minimum qualifier for Natsuki commenting on custom outfits.
    if anniversary_outfit_count >= 3:
        $ anniversary_memories.append("outfits")

    # JN's persistent tracks visit count, but not calendar dates.
    # Technically the log does that... but the log is an editable .txt file.
    if persistent.jn_total_visit_count >= 100:
        $ anniversary_memories.append("visits")

    $ anniversary_memory_seen = dict((name, False) for name in anniversary_memories)
    $ anniversary_memory = jn_anniversary.choose_memory(anniversary_memories)
    if anniversary_memory:

        # This cycles out Natsuki's choice of memory from the upcoming player choices.
        $ anniversary_memory_seen[anniversary_memory] = True

        n 5tdwnvlsbr "There's, um...{w=0.3}{nw}"
        extend 5cchgnfesd " something else I wanted to bring up."

        if anniversary_memory == "visits":
            n 4nchbglsbr "We've been doing this for ages now, haven't we?"
            if persistent.jn_total_visit_count >= 500:
                n 4kspbsledz "You've come back to see me {i}hundreds and hundreds{/i} of times!"
                n 2tchlglelg "Seriously, how have we not run out of things to talk about yet?"
            else:
                n 4kspbsledz "You've come back to see me so many times..."
                n 2klrssl "Guess you've got pretty good taste in company, huh?"
            n 1ksrbgl "It's not like I'm sitting here keeping score every time you show up."
            n 4kdwssl "I just notice when somebody makes room for me in their life."
            n 1kwmsglsbr "And it means a lot that you keep choosing to spend some of yours with me."
            n 2fchsml "Even when I spend some of our time complaining about something ridiculous."
            n 7ttrpul "To be fair...{w=0.5}{nw}"
            extend 6fchgnl " that {i}is{/i} a hobby of mine."

        elif anniversary_memory == "headpats":
            n 2fsrpolsbredz "Don't think I've forgotten all those headpats!"
            if persistent._jn_headpats_total_given >= 1000:
                n 2clrpol "Sheesh, you've done that over a thousand times!{w=0.5}{nw}"
                extend 2fbkgslsbr " A {i}thousand{/i}!"
            elif persistent._jn_headpats_total_given >= 500:
                n 2flrpol "{i}Hundreds and hundreds of times,{/i} [player]!{w=0.5}{nw}"
                extend 2tsqsslsbr " How is my hair still in one piece?!"
            else:
                n 4flrpol "So many dozens of them by now!{w=0.5}{nw}"
                extend 2fsqsmfsbl " What, are you making a hobby out of it?"
            n 1kslsslsbl "...And before you ask...{w=0.5}{nw}"
            extend 1tsqajlsbl " no, I'm not {i}really{/i} complaining."
            n 2tdwsgfsbr "It's just really nice being this comfortable with you."

        elif anniversary_memory == "natsuki_birthday":
            n 1nspbsfedz "I still think about getting to celebrate my birthday with you."
            n 4kllssl "I always thought the best part of a birthday was the cake."
            n 2tsqsml "And don't get me wrong, cake's still a pretty big deal."
            n 1kwmsslsbr "But I really like knowing who I got to share the day with."
            n 1kslsslsbl "That part sticks with me.{w=0.5}{nw}"
            extend 1knmsslsbr " Even after all the decorations are gone."
            n 2fsrbgl "And now I've got an anniversary to celebrate with you, too!{w=0.5}{nw}"
            extend 2nchgnlsbl " Pretty good deal, huh?"

        # Could've left well enough alone but NO, I had to be THOROUGH
        elif anniversary_memory == "admissions":
            n 5ndwbofedz "I like that you let me know what's going on with you."

            if anniversary_admission_count >= 100:
                n 1kwmpulsbr "It really means the world to me how often you've told me how you're doing."
                n 2nchbgl "Guess checking in with each other is second nature by now."
            elif anniversary_admission_count >= 50:
                n 4kwmsslsbr "A few dozen times now, actually."
                n 1kslsslsbr "It's nice that talking about this stuff feels so normal."
            else:
                n 4kslsslsbr "We've had a few of those little check-ins now."
                n 2nsqsml "I like the idea of you making a habit of it."

            # These reactions are naturally based on the player's actual admissions.
            # They prioritize the player's most-used admissions in a lifetime tally.
            # NMA can probably fix that in the future.
            if anniversary_admission_focus == "admission_hungry":
                n 7ttrpul "Although...{w=0.5}{nw}"
                extend 2tsqssl " you {i}did{/i} seem to mention being hungry a lot."
                n 2fchbgl "You'd better be remembering to eat properly, dummy!"

            elif anniversary_admission_focus == "admission_tired":
                n 4kslsslsbr "And I've noticed how often you've told me you're tired."
                n 2fcsajl "You'd better not be pushing yourself too hard!"
                n 2fsqnvl "Though I'm pretty sure we've had this conversation before."

            elif anniversary_admission_focus == "admission_sick":
                n 4kllssl "You've told me when you haven't been feeling well, too."
                n 2fcsflsbr "I don't like knowing you're sick, obviously!"
                n 4kwmsslsbr "But I'd rather know than have you pretend you're fine."

            elif anniversary_admission_focus in (
                "admission_sad",
                "admission_anxious",
                "admission_insecure",
                "admission_ashamed"
            ):
                n 5kllssl "There've been times you've told me you were feeling [anniversary_admission_feeling], too."
                n 4kslsslsbr "I know those aren't always easy things to talk about."
                n 1knmsslsbr "And I'm glad you feel comfortable telling me."

            elif anniversary_admission_focus in (
                "admission_happy",
                "admission_excited",
                "admission_confident",
                "admission_proud"
            ):
                n 1nchsglsbr "And I love hearing when you're feeling [anniversary_admission_feeling]!"
                n 2tsqsml "What? You think I only wanna hear when something's wrong?"
                n 2fchbgl "I wanna hear the good stuff, too!"

            elif anniversary_admission_focus == "admission_angry":
                n 7tllaj "You've come to me when you've been angry, too."
                n 2fsqsml "And you know I've got opinions about that stuff!"
                n 4kslsslsbr "I just hope talking about it helps sometimes."

            elif anniversary_admission_focus == "admission_bored":
                n 2tsqssl "Although I {i}have{/i} noticed you telling me you're bored."
                n 2fcsbgl "Seriously? With {i}me{/i} around?"
                n 1nchlglelg "Ahaha!{w=0.3} Okay, okay.{w=0.5}{nw}"
                extend 1nchgnl " I'm kidding!"

            n 4kllssl "Anyway...{w=0.5}{nw}"
            extend 1knmssl " I like that we can talk about all that stuff."
            n 5kwmsslsbr "Whether it's something big or just a regular old day."
            n 5kkrsglsbr "You can just talk to me, [player]."
            n 2fchbgl "I think we've gotten pretty good at that by now!"

        # Runs off complete custom outfits, not individual wearable components.
        elif anniversary_memory == "outfits":
            n 2nspbsfsbredz "All those outfits you've given me!{w=0.75}{nw}"
            extend 2tsqssl " I've got [anniversary_outfit_descriptor] new outfits to choose from now!"
            n 1nchsglsbr "And that's all thanks to you."

            if anniversary_outfit_count >= 15:
                n 7tllaj "Actually...{w=0.75}{nw}"
                extend 4fcsflsbr " I might need a bigger closet at this rate."
                n 2fsqssl "Seriously, [player]!{w=0.5}{nw}"
                extend 2fchbsl " So many outfits!"
                n 1nsrsml "And that's not even counting my regular stuff!"
                n 2tchbsl "Not bad for a girl who used to wear the same uniform every day, huh?"

            elif anniversary_outfit_count >= 10:
                n 2tllsm "I mean, we're already into double digits!"
                n 2fcsbgl "I've practically got a whole wardrobe to play around with!"
                n 4kslsslsbr "Sometimes I can't even decide what I wanna wear."
                n 2twmbsl "Which is a pretty nice problem to have, actually."

            elif anniversary_outfit_count >= 5:
                n 1nchsml "I've got a pretty decent little collection going!"
                n 7tllaj "And you know what?"
                n 2fchbgl "It's fun having more choices than just my usual clothes!"

            else:
                n 5kslbslsbr "I'm not saying to keep 'em coming, but..."
                n 4fsqsml " you know what?{w=0.75}{nw}"
                extend 4nchbgl " Actually, I am.{w=0.3}{nw}"
                extend 4nchgnl " Keep 'em coming', [player]!"
                n 4fsrbslsbr "I'm kidding, I'm kidding..."

            n 4kllssl "It's nice being able to change up my look now and then."
            n 5kslsslsbl "It's another way I get to express myself, you know?"
            n 1ttrpul "Although...{w=0.75}{nw}"
            extend 2fsqssl " don't go thinking that means you get to pick everything I wear!"
            n 2fcsbgl "I've got my own taste, thank you very much!"
            n 4kslsslsbr "But...{w=0.5}{nw}"
            extend 1kwmsslsbr " I do like that you take an interest in my outfits."
            n 2tsqsml "And if I happen to look especially pretty in one..."
            n 2fchbgl "Well, you're allowed to tell me! Ehehe."

        elif anniversary_memory == "ichi":
            n 4fspbsfedz "All our Ichi games!"
            n 2fchsml "And no, I'm not just bringing them up to brag about winning.{w=0.75}{nw}"
            extend 2fkrbgl " Although, we both know I could."

            # Broke my loose rule about extra labels here just to save on redundant code.
            call jn_anniversary_ichi_reminisce from jn_anniversary_ichi_natsuki_return

            n 4kllssl "I like getting to be competitive around you, [player]."
            n 2fsqsml "Although I'm {i}absolutely{/i} never going easy on you."

        elif anniversary_memory == "love":
            if persistent.jn_player_love_you_count >= 500:
                n 5tspsmf "Do you realize you've told me you love me {i}hundreds and hundreds{/i} of times...?"
                n 5fcsajf "Not that I've counted them all myself!{w=0.5}{nw}"
                extend 4cwmbgf " I'm just saying!"
                n 4fdrpol "Okay, maybe I have.{w=0.5}{nw}"
                extend 2ckrssf " It's not {i}my{/i} fault I remember every time you say it!"
            elif persistent.jn_player_love_you_count >= 250:
                n 5twmssf "You know you've told me you love me hundreds of times, right?"
                n 5csrsmf "You really aren't subtle about it, huh?"
            elif persistent.jn_player_love_you_count >= 50:
                n 5ksqsmf "You've said you love me dozens of times by now."
                n 5fcsajfsbr "That's an awful lot of chances to make your girlfriend blush."
            else:
                n 5kcsajfsbr "When you told me you love me...{w=0.5}{nw}"
                extend 5kkrpufsbr " It made me the happiest girl in the world."
            n 5kslssfsbl "You'd think I'd be completely used to it by now."
            n 5kwmsmfsbl "...Actually, I am.{w=0.5}{nw}"
            extend 5kdwajfsbr " And I like that I can count on hearing it."
            n 4kchbsfsbr "But it still makes me happy every single time, [player]."

        elif anniversary_memory == "compliments":
            if anniversary_compliment_total >= 500:
                n 1tspajledz "You've complimented me {i}hundreds and hundreds{/i} of times now."
                n 2csqsslsbr "I'm starting to think making me blush is one of your favorite hobbies!"
            elif anniversary_compliment_total >= 250:
                $ year_descriptor = "past few years" if anniversary_year >= 2 else "past year"
                n 4kllssl "You've said an awful lot of nice things about me over the [year_descriptor]."
                n 1ksqsml "Like, a {i}lot{/i}.{w=0.5}{nw}"
                extend 4fsqajlsbl " Seriously, when did you get so good at this?"
            elif anniversary_compliment_total >= 100:
                n 4tllssl "You've said really nice things to me so many dozens of times, [player]."
                n 1kchbglsbr "Jeez, do you have a whole list ready or something?"
            else:
                n 4kllssl "You haven't exactly been shy about saying nice things, either."

            # And this is why we calculated the compliment Natsuki has heard the most.
            n 4kllsgf "All those times you told me I was [compliment_descriptor]?"
            n 7kchbgf "I seem to remember you really liked telling me that."
            n 2tsqsml "I mean, I love {i}hearing it{/i},{w=0.5}{nw}"
            extend 2csrbsl " obviously.{w=0.3}{nw}"
            extend 2fsqflf " But only if you mean it!"
            n 3fchsmlsbl "A-{w=0.1}anyway...{w=0.25} you've got {i}excellent{/i} taste in compliments."
            n 1knmssl "Sometimes you notice stuff about me that I wasn't even sure anybody else would notice."
            n 4kslsslsbl "And that's...{w=0.5} really nice, actually."
            n 1kwmssl "I remember those things.{w=0.5}{nw}"
            extend 4kdlbglsbr " More of them than you probably think."
            n 2tsqsmf "So,{w=0.1} don't let it go to your head,{w=0.5}{nw}"
            extend 2tsrbgf " but...{w=0.75}{nw}"
            extend 2nchbsfsbl " you've gotten pretty good at making me feel appreciated."

        n 1ncssml "Heh.{w=0.25}{nw}"
        extend 4kwmssl " It's nice having things I can actually look back on and smile about."

    # Natsuki has so many choices. Why not let the player get in on that action too?
    if len(anniversary_memories) > 1:
        n 1tllajl "Ugh...{w=0.3}{nw}"
        extend 1tcspul " sorry.{w=0.25}{nw}"
        extend 1kslsrl" I've been talking your ear off again, haven't I?"
        n 4ksqsml "Well, this isn't just {i}my{/i} anniversary!"
        n 1knmssl "There's gotta be something you remember, too."

        # Use JNiversary's custom screen for this menu only.
        $ jn_anniversary_original_menu = menu
        $ menu = jn_anniversary_memory_menu

        show natsuki 3tslbsf at jn_left
        menu:
            n "So go on, [player].{w=0.5} Not that I'm fishing or anything, but..."

            "I meant every single time I told you I love you, you know." if not anniversary_memory_seen.get("love", True):
                $ anniversary_memory_seen["love"] = True
                show natsuki 4uskajfsbl at jn_center
                n "W-{w=0.2}what?{w=0.25}{nw}"
                extend 4csqajfsbl " I-{w=0.1}I know that!"
                n 4fcsflfsbr "Jeez, you really don't believe in giving your girlfriend a chance to recover, do you?"

                if persistent.jn_player_love_you_count >= 500:
                    n 5tdwpufsbr "You've said it so many hundreds of times now."
                    n 5tsqajfsbr "I used to think I'd get used to hearing that eventually."
                    n 5nchbsfsbr "But every time still feels like the first time."
                elif persistent.jn_player_love_you_count >= 250:
                    n 5tdwpufsbl "You've said it hundreds of times now."
                    n 5ksrsmfsbl "Like it's the most obvious thing in the world."
                    n 5nchbgfsbr "And... hearing it means so much to me, [player]."
                elif persistent.jn_player_love_you_count >= 50:
                    n 5ksqsmf "You've gotten pretty comfortable saying that, huh?"
                    n 5kslssfsbr "Good. Don't go getting shy about it now!"
                else:
                    n 5kllsmfsbr "And you know what? It doesn't need a big speech."
                    n 5kwmsmf "Hearing you say it means plenty on its own."

                n 4kslssfsbl "...I wouldn't want you to say it if you didn't mean it."
                n 5kwmsmf "And I know you do.{w=0.5}{nw}"
                extend 5nchbgfsbl " That's what makes hearing it so good."
                n 5ksqssfsbr "I love you too, [player].{w=0.5}{nw}"
                extend 2kcsbsf " Every single time."

            "You deserve all those compliments. You constantly earn them." if not anniversary_memory_seen.get("compliments", True):
                $ anniversary_memory_seen["compliments"] = True
                show natsuki 1uskajfsbl at jn_center
                n "H-{w=0.2}hey!{w=0.5}{nw}"
                extend 2fsqajfsbl " You can't just give me {i}another{/i} one while we're talking about them!"
                n 4kslsslsbl "...Although I guess that kind of proves your point."

                if anniversary_compliment_total >= 500:
                    n 2tdwpufsbr "You've told me those nice things so many hundreds of times now."
                    n 2tcsfll "Can you even look at me without finding something nice to say?"
                    n 4csrsslsbr "N-{w=0.2}not that I'm telling you to stop!"
                    n 1kwmssl "Well, I'm not gonna lie to you.{w=0.5}{nw}"
                    extend 1kdwsrl " They're...{w=0.3}{nw}"
                    extend 1ksrbgf " really nice."
                elif anniversary_compliment_total >= 250:
                    n 4fsqajlsbr "And don't think I haven't noticed how often you do this!"
                    n 2tdwpufsbl "It's been, what?{w=0.5}{nw}"
                    extend 2kchbgfsbl " Hundreds of times now?"
                    n 1ksrbgfsbr "You're too good at catching me off guard."
                    n 7fsrbofsbl "Maybe a little {i}too{/i} good..."
                elif anniversary_compliment_total >= 100:
                    n 2tsqsmf "You're getting pretty good at those, you know."
                    n 7ksrpufsbl "Maybe a little {i}too{/i} good..."
                else:
                    n 4ksrsmfsbl "And you know I've noticed."
                    n 2kdrnvfsbr "You're not exactly subtle about making me feel special!"

                n 3ksqbol "So... thanks, [player].{w=0.5}{nw}"
                extend 1kwmssl " I notice the nice things you do, too."

            "I loved being here for your birthday." if not anniversary_memory_seen.get("natsuki_birthday", True):
                $ anniversary_memory_seen["natsuki_birthday"] = True
                show natsuki 1usksslsbl at jn_center
                n "...You remember that?"
                n 4kllssl "I mean, of course you do.{w=0.5}{nw}"
                extend 4kslsslsbr " It's not like I'm exactly quiet about birthdays!"
                n 1kwmssl "I had a really good time sharing mine with you."

            "I really appreciated what you did for my birthday." if not anniversary_memory_seen.get("player_birthday", True):
                $ anniversary_memory_seen["player_birthday"] = True
                show natsuki 1uskajfsbl at jn_center
                n "W-{w=0.2}wait, really?{w=0.5}{nw}"
                extend 2fcsajlsbr " I mean, of course I wanted to do something nice for you!"
                n 2fsqssl "You remember that cake, right?"
                n 1nchbgl "I was pretty proud of that!"
                n 4kslssfsbl "And...{w=0.5}{nw}"
                extend 5kdwsslsbr " I really hoped you'd enjoy the surprise."
                n 5kwmsmfsbl "You deserve to feel special on your birthday, [player]."
                n 2fsqsmfsbl "So don't think I'm gonna stop making a fuss over you!"
                n 1nchbgl "You've got plenty more birthdays coming, after all!"

            "Definitely not forgetting how much you like headpats." if not anniversary_memory_seen.get("headpats", True):
                $ anniversary_memory_seen["headpats"] = True
                show natsuki 2uwdssfsbl at jn_center
                n "E-{w=0.2}excuse me?!{w=0.5}{nw}"
                extend 2fsrssfsbl " Who said anything about {i}liking{/i} them?!"
                n 4ksrsmf "...Okay, fine, maybe I like them a little."
                n 1ksqsl "Sometimes more than a little."
                n 2fsqsrl "You're lucky my hair survives all of those.{w=0.75}{nw}"
                extend 2cchlglelg " Or this would be a {i}very{/i} different conversation."

            "Well, all that Ichi comes to mind..." if not anniversary_memory_seen.get("ichi", True):
                $ anniversary_memory_seen["ichi"] = True
                show natsuki 1uskajlsbl at jn_center
                n "W-{w=0.2}wait, really?{w=0.5}{nw}"
                extend 2tsqsmfsbl " The card games?!"
                n 2cchlglelg "Ahaha!{w=0.5}{nw}"
                extend 2nwmsgfsbl " Okay, yeah.{w=0.5}{nw}"
                extend 2fsqsml " We've had some pretty good ones!"
                call jn_anniversary_ichi_reminisce from jn_anniversary_ichi_player_return
                n 4kslsslsbl "...Thanks for remembering those, [player]."
                n 1kwmssl "It's nice making memories with somebody I can be silly around."
                n 2fsqsml "Even if you {i}can{/i} be a complete pain to play against!"

            "I love telling you how I'm feeling." if not anniversary_memory_seen.get("admissions", True):
                $ anniversary_memory_seen["admissions"] = True
                show natsuki 1uskajfsbl at jn_center
                n "H-{w=0.2}huh?{w=0.5}{nw}"
                extend 4kllssl " Well, yeah."
                n 1kwmsslsbr "I like hearing about your day, [player]."

                if anniversary_admission_count >= 100:
                    n 1kwmsslsbr "We don't even have to make a big thing of it anymore."
                    n 2tsqsml "A bad morning, a good afternoon... I wanna hear it all."
                elif anniversary_admission_count >= 50:
                    n 2ksqsml "We've really gotten into the habit of checking in, huh?"
                    n 4kwmssl "I like having that with you."
                else:
                    n 4kwmsslsbr "You don't have to make a big thing of it every time."
                    n 2fsqsml "Even a little update tells me something about your day."

                if anniversary_admission_focus in (
                    "admission_sad",
                    "admission_anxious",
                    "admission_insecure",
                    "admission_ashamed"
                ):
                    n 5kslsslsbl "Especially when it's something you aren't feeling great about."
                    n 1knmsslsbr "I know you've trusted me with things like that."
                    n 4kslsslsbr "And I take that seriously."

                elif anniversary_admission_focus in (
                    "admission_hungry",
                    "admission_tired",
                    "admission_sick"
                ):
                    n 2fsqssl "Although sometimes I think I oughta start checking whether you're taking care of yourself!"
                    n 4kslsslsbr "You know I worry about that stuff."

                else:
                    n 2fchbgl "Besides, I like hearing the good stuff, too!"
                    n 4kwmssl "It's nice getting to share those everyday moments."

                n 2fsqssl "And hey, you don't have to agree with everything I say!"
                n 4kllssl "That's not what being close to somebody's about."
                n 1kwmsslsbr "I'm just glad we're comfortable talking about this stuff."
                n 2ksqajl "So keep me in the loop, okay?"
                $ chosen_tease = jn_utils.getRandomTease()
                n 2fchbgl "I wanna know what's going on with my favorite [chosen_tease]!"

            "I love all the outfits you've got to choose from!" if not anniversary_memory_seen.get("outfits", True):
                $ anniversary_memory_seen["outfits"] = True
                show natsuki 1uskajfsbl at jn_center
                n "H-{w=0.2}hey!{w=0.5}{nw}"
                extend 2ksqssfsbl " You've really been paying attention, huh?"
                n 7tllaj "Well...{w=0.5}{nw}"
                extend 4ksrsmfsbr " I guess I {i}do{/i} have [anniversary_outfit_descriptor] custom outfits now."

                if anniversary_outfit_count >= 15:
                    n 2fcsbgl "At this point, I'm practically spoiled for choice!"
                    n 1nchbslsbl "And I'm not complaining!"

                elif anniversary_outfit_count >= 10:
                    n 2tsqsml "I've got enough choices to keep things interesting for ages!"

                elif anniversary_outfit_count >= 5:
                    n 1nchsml "It's a pretty nice collection, actually."
                    n 2ksrbgl "I'm starting to get used to having all these options."

                else:
                    n 4kwmssl "It's nice having a few different things to wear."
                    n 1nchbgl "Makes a change from my usual clothes!"

                n 4ktlslsbr "I like knowing I can change things up when I feel like it."
                n 1kwmsslsbr "...But I'm glad you like seeing me try on those outfits, [player]."
                n 2fchbgl "You've got good taste! Ehehe!"

            "I genuinely love coming to visit you." if not anniversary_memory_seen.get("visits", True):
                $ anniversary_memory_seen["visits"] = True
                show natsuki 1uskajlsbl at jn_center
                n "H-{w=0.2}hey, that's not fair!{w=0.5}{nw}"
                extend 4fsqajlsbr " I was asking for a memory, not a sneak attack!"
                if persistent.jn_total_visit_count >= 500:
                    n 4kslsslsbr "And after hundreds and hundreds of times you've come to see me..."
                    n 2csqsml "You still know how to catch me off guard with one sentence!"
                else:
                    n 2fsqsml "But I guess you really do like spending time with me, huh?"
                n 4kslsslsbl "...You know, I'm glad it's something you actually look forward to."
                n 1kwmsslsbr "It's not the number I care about.{w=0.5}{nw}"
                extend 1kwmssl " It's that you want to be here."
                n 2ksqajl "And for the record?{w=0.5}{nw}"
                extend 1knmsslsbr " I look forward to seeing you, too.{w=0.45}{nw}"
                $ chosen_tease = jn_utils.getRandomTeaseName()
                extend 4ctlbsl " Even when you're being a [chosen_tease]."

        # Restore JN's original menu handler.
        $ menu = jn_anniversary_original_menu

        n 1ncssml "...{w=0.5}{nw}"
        extend 4kwmsslsbr "You know what?"
        n 1klrsslsbr "I'm really glad you brought that up."
        n 2csqsml "This celebration's way more fun when I can hear what {i}you{/i} remember, too."

    # We quickly calculate the season in which the player first met Natsuki.
    python:
        anniversary_meeting_season = (
            "Winter" if persistent.jn_first_visited_date.month in (12, 1, 2) else
            "Spring" if persistent.jn_first_visited_date.month in (3, 4, 5) else
            "Summer" if persistent.jn_first_visited_date.month in (6, 7, 8) else
            "Autumn"
        )

    # Just a fun little nod, based off that calculation.
    # If the player met Natsuki during their favourite season, why not reference it?
    if persistent.jn_player_favourite_season == anniversary_meeting_season:
        n 1tllajl "Oh!{w=0.25} By the way...{w=0.5}{nw}"
        extend 4ksqsml " you told me [anniversary_meeting_season] was your favorite season, right?"
        n 1knmssl "That's the time of year you first came here, too."
        n 4kslsslsbl "I dunno... I think that's kind of sweet."
        n 1kwmssl "Maybe you had a good reason to like it even before we met."
        n 1ksqsml "But now I've got one, too!{w=0.5}{nw}"
        extend 2fsqsslsbr " Just don't get smug about it."

    n 1ncssml "I...{w=0.25}{nw}"
    extend 4kllssl " know I'm a chatterbox today, but there's...{w=0.5}{nw}"
    extend 4fdlbgf " {i}something else.{/}"
    
    show natsuki 1tsqfl at jn_left
    menu:
        n  "And I really mean this, so no interrupting with a joke, got it?"

        "[n_name], I wouldn't dream of it.":
            show natsuki 4kslsslsbl at jn_center
            n "Good, because...{w=0.3} well."

        "But... I had a really good one ready to go.":
            show natsuki 4fsqflfsbl at jn_center
            n "Can it, [player].{w=0.5}{nw}"
            extend 6fsqbsl " We can swap the wordplay later."

    if anniversary_focus == "noticed":
        n 1kllssl "You said you liked the little sides of me that other people miss."
        n 4kwmssl "I think I like having somebody who wants to see them."
    elif anniversary_focus == "quiet":
        n 4kllssl "Anyway, the quiet moments you mentioned?{w=0.5}{nw}"
        extend 1kwmsml " I like those, too."
        n 1kwmsslsbr "I don't have to fill the silence just to know a certain somebody I care about's still here."
    elif anniversary_focus == "future":
        n 4kwmsslsbr "I liked what you said earlier about there being more to learn about each other."
        n 2fcssml "I've got so many things I haven't told a certain somebody yet.{w=0.5}{nw}"
        extend 2nchbsf " Better keep up!"
    else:
        n 5kslssfsbl "Anyway...{w=0.3} I just wanted to say it's a pretty wonderful feeling, feeling appreciated like this."
        n 5fdwsmfsbl "Even if {i}somebody's{/i} determined to make me blush about it."

    if Natsuki.isLove(higher=True):
        n 5kslajfsbr "And... I'm glad that somebody's my partner."
    else:
        n 5nslssl "And I'm glad that somebody's my best friend."
    n 5kwmsml "Call me sappy, but...{w=0.5}{nw}"
    extend 5kcsbgf " I think that's something worth celebrating all by itself."


# =============================================================================
# 05. FINALE: Poem and Conclusion
# =============================================================================
# Not much to say here! What you see, what you get, etc.

    python:
        anniversary_unread_poems = jn_poems.JNPoem.filterPoems(
            poem_list=jn_poems.getAllPoems(),
            unlocked=False,
            holiday_types=[jn_events.JNHolidayTypes.jn_anniversary]
        )
        anniversary_poem = (
            renpy.random.choice(anniversary_unread_poems)
            if anniversary_unread_poems else None
        )

    if anniversary_poem:
        n 4fcsflsbr "...Which,{w=0.2} I guess,{w=0.2} brings me to my gift.{w=1}{nw}"
        extend 1kslsslsbl " I got you a little something."
        n 1tdwbgl "It's a little silly.{w=0.5}{nw}"
        extend 1knmbslsbr " But I like it."
        n 4kslsslsbr "And I want you to have it."
        n 4kwmsslsbr "Take your time, okay?{w=0.5}{nw}"
        extend 1kchsglsbr " I wanna hear what you think."
        n 1kdwbsfsbr "Here, [player]...{w=0.5}{nw}"
        extend 1kslnvfsbr " this is for you."
        # Quiet the music while the player reads Natsuki's poem.
        $ renpy.music.set_volume(0.2, delay=1.0, channel="music")
        call show_poem(anniversary_poem) from holiday_jn_anniversary_poem_return
        # Restore the normal music level when the poem closes.
        $ renpy.music.set_volume(1.0, delay=1.5, channel="music")

        n 1ksqsslsbl "...Well?"
        show natsuki 2fchgnl at jn_left
        menu:
            n  "Don't just sit there looking at me! Say something!"

            "You put so much of yourself into this, [n_name].":
                show natsuki 1kwmbslsbr at jn_center
                n "...Good.{w=0.5}{nw}"
                extend 4nchbgl " That's exactly what I was going for."
                n 5kdwsml "I wanted it to sound like something only I would've written for you."

            "Ha! I forgot how much you like to break the rules at the end.":
                show natsuki 1ksrsmfsbl at jn_center
                n "...Right!"
                n 4kwmssl "I was kinda hoping you'd like that part."
                n 1kslsslsbl "It's the bit I kept coming back to when I was writing."
                n 5kwmsmfsbl "...Thanks for taking it seriously."

            "I'll treasure this. It's one of the sweetest gifts I've ever received.":
                show natsuki 1uskajfsbr at jn_center
                n "W-{w=0.2}what?!{w=0.25} Really?"
                n 2fllpofsbr "Sounds like somebody needs better friends..."
                n 1kwmsmf "...But I'm glad you wanna keep it.{w=0.5}{nw}"
                extend 1kchsglsbr " I was hoping you might say something like that."

            "I love how playful it is. It's just like you.":
                show natsuki 3nchgnlsbl at jn_center
                n "Ahaha!{w=0.25} Good!"
                n 2tsqsml "What's the point of writing about fries and pies otherwise?"
                n 1kslsslsbr "And I really did mean the nice part at the end, okay?"

        n 1knmssl "It's nice making something and knowing who's gonna appreciate it."
        n 1kchsml "Thanks for reading it.{w=0.5}{nw}"
        extend 4twmbglsbl " Seriously."

    else:
        n 1nchsml "Oh, and I'm still working on a new poem for you."
        n 2fsqsml "It hasn't reached my standards yet, but it will."
        n 4kwmssl "I like writing for you.{w=0.5}{nw}"
        extend 4kllssl " I wanna make sure it's worth sharing."

    if Natsuki.isLove(higher=True):
        $ chosen_endearment = jn_utils.getRandomEndearment()
        n 5kwmsmfsbr "I love you, [chosen_endearment]."
        $ chosen_descriptor = jn_utils.getRandomDescriptor()
        n 5ksqsmf "And I think you're [chosen_descriptor], you know."
        n 5kllssfsbl "I like being able to say that without worrying how it sounds."
        n 5ksqsmfsbr "Even if I do get embarrassingly mushy sometimes."
    else:
        n 5ksgsmlsbl "You're my best friend, [player].{w=0.5}{nw}"
        extend 5kwmbgfsbl " I'm really glad we met."
        n 5fcsajl "And I like that you let me know what's going on with you, too."
        n 5ksqsml "I'm still gonna give you a hard time sometimes.{w=0.5}{nw}"
        extend 5kslssf " That's part of the deal."

    n 1kwmsml "Happy anniversary again, [player]."
    # Redundant, but just in case: clear the old confetti before brining it back.
    hide confetti
    play audio smack
    show confetti falling at jn_confetti_fall zorder JN_PROP_ZORDER
    $ jnPause(1)
    n 2fchbslsbr "That never gets old.{w=0.5} Ehehe."
    n 2fchgnl "Now, come on!{w=0.5}{nw}"
    extend 4kslsslsbr " We've still got some time to enjoy!"
    hide confetti
    show confetti desk zorder JN_PROP_ZORDER

    # Pack away the anniversary cake and restore the original desk item.
    # And a little audio SFX. You know, for immersion.
    show black zorder JN_BLACK_ZORDER with Dissolve(0.5)
    $ renpy.music.set_volume(0.2, delay=1.0, channel="music")
    $ jnPause(1.5)
    play audio glass_move
    $ jnPause(0.5)
    play audio drawer
    # Remove the cake from Natsuki's desk.
    $ Natsuki._desk_centre = anniversary_previous_desk_centre
    # Also clear any separately displayed cake prop.
    hide prop
    $ jnPause(0.5)
    play audio drawer
    $ jnPause(1.5)
    $ renpy.music.set_volume(1.0, delay=1.5, channel="music")
    # This switches in a warmer Natsuki expression for ch30.
    show natsuki 3twmsmf at jn_center
    hide black with Dissolve(0.5)

    # ~Fin
    $ jn_anniversary.finish(anniversary_year, anniversary_poem, late)
    return


# =============================================================================
# 06. SPOILERS: POEMS
# =============================================================================
# For any JN custom poetry, vanilla DDLC and the side stories are my north star.
# I'm a ghostwriter by trade, but I think I do a decent job mimicking Natsuki's 
# simple yet poignant style. Though, YMMV!

init 3 python in jn_anniversary:
    import store.jn_poems as jn_poems

    register_poem = getattr(jn_poems, renpy.munge("__registerPoem", jn_poems.getAllPoems.func_code.co_filename))

    # Future poems will use the same holiday_type but a new reference_name. Simple!
    register_poem(jn_poems.JNPoem(
        reference_name="jn_anniversary_unlike_you",
        display_name="Unlike You",
        holiday_type=jn_events.JNHolidayTypes.jn_anniversary,
        affinity_range=(jn_affinity.ENAMORED, None),
        # As my first ghostwritten Natsuki poem, I decided to aim for something shorter
        # and sweeter than her 2–3 lengthier compositions. Instead, I chose to go for
        # Natsuki's non-traditional stanzas and rhyming structures, while sticking to
        # specific syllable counts——and rhymes tethered like string between the stanzas.
        # 
        # Would you believe this was originally meant to be closer ot "Eagles Can Fly"?
        poem=(
            "You're not the kite in my skies\n"
            "Because kites can't go very high.\n"
            "They can't even reach a cloud.\n"
            "And when it's too windy they blow everywhere.\n"
            "Kites are a lot of work.\n"
            "Unlike you.\n"
            "\n"
            "You're not the bite of my fries\n"
            "Because fries are over too soon.\n"
            "They can't even feed a crowd.\n"
            "And then they get stale in minutes, I swear!\n"
            "Fries are a lot of bother.\n"
            "But not you.\n"
            "\n"
            "You're not the height of my pies\n"
            "Because pies always want to slump.\n"
            "They make me grumble aloud.\n"
            "And when you are baking, they need too much care.\n"
            "Pies are a lot of trouble.\n"
            "Not like you.\n"
            "\n"
            "If you were this kite, you'd sail the stars.\n"
            "If you were these fries, you'd crunch just right.\n"
            "If you were this pie, you'd be the best.\n"
            "And I think you know the rest.\n"
        ),
        paper="pink_floral",
        font_size=20
    ))

# Will add poems for additional anniversaries later. This will likely randomize
# the chosen poem while obviously disqualifying any previously-seen poetry.


# =============================================================================
# 07. BONUS: ICHI (SHARED LABEL)
# =============================================================================
# This was aggravating to manage, so I've slapped it into its own label here.
# This label won't get called unless Ichi has 15+ recorded completed rounds.

label jn_anniversary_ichi_reminisce:
    # Good lord, 250+ games played...?
    if anniversary_ichi[0] >= 250:
        n 2csqbgl "You'd think we'd have run out of tricks by now, wouldn't you?"
        n 1cchbsl "Well, tough luck!{w=0.5}{nw}"
        extend 4fchgnf " I've still got ways to beat you!"
        n 2cwmsgf "And I still love seeing what you come up with, too."

    # Whoa, 100-249 games played?
    elif anniversary_ichi[0] >= 100:
        n 1uskajl "I mean, we've played at least a hundred rounds together now!{w=0.5}{nw}"
        extend 1kchbsl " A hundred!"
        n 2fsrsgl "Well,{w=0.25}{nw}"
        extend 2fsqsgl " don't you worry.{w=0.5}{nw}"
        extend 2fchbgl " I've still got plenty of tricks up my sleeve."

    # Dang, 50–99 games played?
    elif anniversary_ichi[0] >= 50:
        n 1tllajl "We've played {i}plenty{/i} of rounds together now, you know."
        n 2nchbgl "Dozens of them!{w=0.3}{nw}"
        extend 2ksqssl " And, just so you know...{w=0.5} I've got plenty more where that came from."

    # Cool, 15–49 games played?
    else:
        n 1nwmsml "We've already played quite a few rounds together."
        n 4fchbgl "And we keep surprising each other."

    # Has the player got a clear Ichi victory lead...
    if anniversary_ichi[3] == "player":
        n 2csqfl "And yeah,{w=0.3} {i}maybe{/i}{w=0.3} you've won more of them than me.{w=0.5}{nw}"
        extend 1fsgpolsbr " I've noticed!"
        n 2fcsajl "Don't get comfortable!{w=0.5}{nw}"
        extend 4fsqssl " The moment you start getting sloppy, that's when I'll get you."

    # ...Or does Natsuki?
    elif anniversary_ichi[3] == "natsuki":
        n 1nchbgl "And I've still got a big lead on you.{w=0.5}{nw}"
        extend 2nchgnfsbl " Ehehe!"
        n 4fsqsml "Better shape up soon, [player].{w=0.5}{nw}"
        extend 1kwmsml " Though, I really just love playing with you."

    # Of course, maybe their scoreboard's neck-and-neck
    else:
        n 1tsgsgl "And neither of us can really claim the crown yet, can we?"
        n 2fcsbgl "It's pretty neck-and-neck.{w=0.5}{nw}"
        extend 2fchgnl " That's what makes it fun!"

    return
