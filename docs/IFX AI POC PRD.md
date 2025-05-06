# Intelligent Fan Experiences AI POC: Product Requirements Document

**Date Started:** Apr 2, 2025  
**Last Update:** May 2, 2025  
**Owners:** Alex Liss, Christopher Bunker  
**AI Engineer**: Ryan Balch  
**Technical Advisors:** Bobby Knapp, Jon Hackett  
**Front End Designer**: Fill In 

## Situation

From a strategic perspective, Intelligent Fan Experiences (IX) can be a game changer for Huge. It's more than a new offering—it's an on-ramp into an industry primed for reinvention. Sports organizations across leagues are grappling with aging fan bases, fragmented attention, and underleveraged data. IX gives us a way to frame AI not as a back-office efficiency play, but as a top-line growth lever tied to fan acquisition, retention, and monetization by appealing to new audiences (younger Millennial and Gen Z) with AI-native experiences. It positions Huge as a strategic innovation partner, not just a vendor.

It's also a high-emotion, high-visibility entry point into a massive global industry. By showing up with IP that directly addresses sports clients' most urgent fan challenges, IX can unlock net-new conversations across leagues, teams, venues, and sponsors. It's a wedge we can use to open doors, prove our value fast, and expand from there—into media, entertainment, and beyond.

From a technical perspective, in order to scale up IX, we need to scale up our GTM operations especially around demonstrating our capabilities to win new business. Most of our amazing AI work (Google, BBVA, Schneider, Hublot, etc) is under NDA and can't be shared. So, let's proactively make a publicly demo-able AI application, which encapsulates our IX principles, to help accelerate our sales pipeline.

### Our hypothesis is that:

- By developing thought leadership content alongside AI demos we can SHOW (not tell) how we build IX and get clients excited about buying it  
- If we build proactively then helps us scale up delivery – leveraging an MCP-centric architecture and giving us an additional instance of our MCP / IX Accelerator

## Objective

Deploy a one-two punch of an Intelligent Fan Experiences blog piece / presentation keynote along with an AI demo, with the AI demo to achieve the following:

### \[Experience Objective\]

Demonstrate a novel and impactful approach to solve existing challenges across the fan journey including:

- **Awareness:** reach new fans, make them aware of the team / sport / league  
- **Attraction:** bring a fan to take action (e.g. watch a game, attend a game, buy merch, attend a watch party)  
- **Attachment:** bring a fan to take repeated action  
- **Allegiance:** fan becomes an evangelist and recruits others to become fans

### \[Sales Pipeline Objective\]

Get clients interested in this, both new logos and organic, once the thought leadership \+ AI demo is complete, we can generate buzz, leads, and set-up inbound briefs through content distribution:

- E.g. a IFX whitepaper deployed online (measure reach, site visits)  
- Gated form to Unlock IFX for sports (capture emails, quantify warm leads)  
- Within the IFX white paper there's a link fo the AI demo site (measure user engagement with that)

## Experience Principles

### Form Factor & Distribution:

For the purposes of doing a public demo, this AI experience will live as a website, (Thought starter – let's consider how this could look like a mobile phone).

As part of the storytelling in the thought leadership piece, we should imagine this AI experience living with the existing platforms of the Team / League/ Fan Platform. (See FIFA 24 pitch example of a sparkly AI button a user can click while engaging with existing app / web ecosystem.) It should be mobile-native to reach younger Millenials and Gen Z, we know from our \[FILL IN\].

When starting the experience we would also ask the user to select one of a series of pre-created synthetic fan profiles. This allows us to demonstrate the unique capabilities of the experience when personalizing to user preferences, while also NOT requiring the human user to enter their personal information into the experience.

### Non-negotiables:

- Snackable  
- Seamless (natural language)  
- Smart (dynamic for what you need at that moment)  
- \[Shoppable – not for this demo\]

### Core IX Principles:

The core principles of IX are Conversational, Anticipatory, Personal, and Future Ready. As we look to deploy this in Q2 2025, we need to ensure it's sufficiently on the leading edge of AI innovation, including:

#### Multimodal outputs (images, assets)

It's not enough to just connect some data to an LLM and let people chat with it. We need it to ✨, something like the following:

**Old** 👎

```
User: How did the 49ers do in their last game?
AI: The 49ers lost to the Minnesota Vikings by a score of 23-17 on September 10, 2024.
```

**New** 😇

```
User: How did the 49ers do in their last game?
AI: 
```

(See example recap components on this page: [https://sports.yahoo.com/nfl/scoreboard/?confId=\&dateRange=18\&schedState=2](https://sports.yahoo.com/nfl/scoreboard/?confId=&dateRange=18&schedState=2))

**AI Response:**  
*The 49ers lost on the road to the Minnesota Vikings by a score of 23-17 on September 10, 2024\. Click the link above to see the highlights.*

The principle that this illustrates is that the AI output is not just multimodal and also dynamic to the user query. For example, a search for 'tell about the star players on the 49ers' would return an image of the player's bio pic and stat snippets, link to social media handles, etc.

#### Personalized

- Personalize the response to the users query based on profile and contextual data  
- For example, let's imagine a (female?) user engaging with the app and looking to learn more about the players. Based on the user's preferences, we'd know they follow Olivia Copelo (fashion influencer / married to running back Christin McCaffrey), and that recommendation is seamlessly surfaced to the user  
- For exploration: when a user starts the experience they select their level of experience (e.g. novice / intermediate / expert) – customize the responses, the content, the functionality based on that  
- We can show people what it looks like to 'graduate' from one level to the next, how they accrue points to 'level up'

#### Conversational

- The AI experience will be multi-modal and chat-oriented. When the user selects a pre-build persona they will have that fan's preferences and history loaded (on the back-end we'll try implementing this with Zep for agent conversational memory).  
- We will also increment that memory graph with the actions taken by the user in the course of the session(s).

#### Back-end: MCP-centric structure aligned with our IX Tech Accelerator

- The features of the app are built as MCP servers which are called by this app but can be reused across other apps, services, integrations, etc.

## Scope

### Primary Use Cases & Key Features:

| Stage | Job to be Done | Feature |
| :---- | :---- | :---- |
| **Awareness** | Come across something exciting | 1\. Team Search (E) |
|  | Get the vibe of the team | 1\. Team Search (A/B) |
|  | See what everyone's talking about | 1\. Team Search (C/D) |
| **Attraction** | Understand the rules | 4\. Rule Search |
|  | Learn about key players | 2\. Player Search |
|  | Start following the sport | TBD – Need to refine this – get notifications? |
| **Attachment** | Feel emotionally invested | 3\. Game Search |
|  | Personalized content | 0\. Persona Selection |
|  | Interact with other fans | 5\. Fan Community Search |
| **Allegiant** | TBD |  |

## Feature List

### 0\. Persona Selection

When the user starts the app they will be presented with 3 fan personas which will represent novice/casual, intermediate/engaged and advanced/super fan profiles. The app will respond differently based on the selected profile.

(WIP thought: implement this through Zep so entering a persona\_id selects a prebuilt memory and set of preferences for that persona, which comes through conversationally as well as in which content assets are retrieved for each user)

**Personalization routes:**

- Based on the user's platforms e.g. if someone is on IG, we should them IG profiles  
- Ability to opt in / opt out  
- Log in through your social platform  
- Bring their interests into the app and then personalization based on that

### 1\. Team Search

Features 1-5 allow the user to enter a query in natural language regarding the topic of interest (Team, Players, Games, Rules, Fan Communities). Results will be retrieved from the web or the knowledge graph and displayed to the user in a dynamic layout depending on what they are searching for.

**Types of searches and format:**

- **Overview \[Novice\]**  
  - Tell me about the 49ers  
- **Season Recap \[Novice\]**  
  - How did the 49ers do last year  
- **Trending News / Key Stories \[Intermediate\]**  
  - How did the 49ers do in the offseason  
- **Outlook for next year \[Intermediate\]**  
  - Are the 49ers going to be good this year  
- **Best plays of last year \[Novice\]**  
  - Show me top plays from last year  
- **\[Advanced queries TBD – something about the draft?\]**

**Component:**

- Web search to pull content  
- Display as Text widget with image / video previews

### 2\. Player Search

**Types of Searches:**

- **Overview (Default) \[Novice\]**  
  - Who is the starting QB?  
  - Who are the best players?  
- **Stats by Game \[Intermediate\]**  
  - What was Deebo Samuels best game last year?  
- **Performance by Game \[Advanced\]**  
  - How accurate is Brock Purdy's deep ball?

**Component:**

- Graph search to pull content  
- Display as Text widget with image / video previews

### 3\. Game Search

**Types of Searches:**

- **Overview (Default) \[Novice\]**  
  - What was the 49ers record last season?  
- **Search for a Specific Game \[Intermediate\]**  
  - How did the 49ers do against the Dolphins?  
- **Game Results/Top Plays \[Advanced\]**  
  - How did the 49ers passing attack perform against man vs zone coverage?  
  - What was the critical moment in the 49ers loss to the Seahawks?

\[reference – Key moments / highlights / analysis (see feed sort of like this article) https://sports.yahoo.com/live/49ers-dominate-early-turn-aside-seahawks-comeback-with-key-int-of-geno-smith-in-36-24-win-231533727.html – but keep it to one key play per game\]

### 4\. Rule Search

RAG from the rulebook \+ general LLM reasoning  
TBD / low priority on this feature

## Technology Approach

### App Structure, Approach & Key Questions

- The app is hosted on HuggingFace Spaces  
- The underlying data structure is a graph database in neo4j

#### App user session management

- The user will select pre-set personas (e.g. with attributes and preferences implemented through a Zep knowledge graph)  
- The user will click on a persona (button select) to set global variables that will influence application behavior  
- Key question – how to create a multi-screen app in gradio so that once the clicks the persona button that screen will disappear enabling them to experience the chat app?

#### Building dynamic UI components will happen as follows:

- Foundation layer is a graph database (Neo4j)  
- Most of the features and use cases will be supported by calling the graph and its linked assets and displaying that to the user  
- Key question – what is the best way to integrate images with a neo4j database? E.g. a player database that also can display a headshot (image) of each player

#### MCP Server integration – DE-PRIORITIZED UNTIL MCP GATEWAY IS BUILT 

- For modularity I'm imagining that that 'back end' functions (e.g. retrieve data from neo4j) would be  
- Can MCP servers be called client-side by the Gradio application?  
- There is a POC on github with 54 stars 😅  
- Key question – how to integrate an MCP serveer into a web app specifically in gradio?

#### Building custom Gradio UI

- Once i retrieve data payload from MCP functions I want to display as a front-end html component in gradio in response design  
- Key question – how to build responsive design HTML components in gradio?

### Asset Requirements for Multi-modal output

#### Team Search

- Team highlights – e.g. best plays of the season, best plays against NFC west [https://www.youtube.com/playlist?list=PLBB205pkCsyvZ6tjCh\_m5s21D0eeYJ8Ly](https://www.youtube.com/playlist?list=PLBB205pkCsyvZ6tjCh_m5s21D0eeYJ8Ly)

#### Player Search

- Player headshots, e.g. from this page [https://www.49ers.com/team/players-roster/](https://www.49ers.com/team/players-roster/)  
- Player highlight videos / Top 10 Plays e.g. from this page [https://www.youtube.com/playlist?list=PLBB205pkCsyvZ6tjCh\_m5s21D0eeYJ8Ly](https://www.youtube.com/playlist?list=PLBB205pkCsyvZ6tjCh_m5s21D0eeYJ8Ly)  
- Play social media handles and follower counts, MIGHT be as easy as pulling from Google Search links but need a robust process / pattern for that

#### Game Search

- Game recap videos e.g. from this page [https://www.youtube.com/playlist?list=PLBB205pkCsyvZ6tjCh\_m5s21D0eeYJ8Ly](https://www.youtube.com/playlist?list=PLBB205pkCsyvZ6tjCh_m5s21D0eeYJ8Ly)

## Phases of Development

1. Initial POC being built on Streamlit (v1 is live here)  
2. Replatform to Gradio to build custom UI components  
3. Create Dynamic UI components as MCP servers  
4. Leverage GradioUI as presentation layer to user  
5. Consider mobile-native 'frame' within demo site  
6. Apply Huge Branding for the last mile

## Backlog

- Improve performance of gradio (revisit after replatforms back end)  
- Source data to enable features  
- Rebuild langchain tools as MCP servers  
- Build dynamic widgets for F/E display  
- Test with freeplay and ship 👀‼️

## Success Criteria

- First Release / stabilizing inital deployment  
- Scaling strategy (think of sales funnel)  
- Number of clients registered for white paper paper  
- Number of clients logged in to AI experience

## Timeline

Desired public release: May 29, 2025

### Proposed phases of work:

#### Sprint 1: Needfinding, Feature Definition and Prioritization (March 31 \- April 11\)

- Product work  
- Heuristic Analysis / Beacons completed ✅  
- initial feature set and and map out workload for rest of Sprint 1 ✅  
- Define what experience 'slices' and features makes an IFX (from a fan experience problem \-\> technology solution) ✅  
- Prioritize those features ✅  
- Define requirements and acceptance criteria ✅  
- Data discovery \+ collection ✅

#### Sprint 2: Back End Data Staging & Display (April 14 \- April 25\)

- 🔃 Get all data needed  
- Build new features  
  - ✅Team Search  
  - ✅Player Search  
  - ✅Game Recap Search  
- Work on displaying through dynamic components in gradio  
- Next demo April 22  
- ✅Implement Persona and memory

#### Sprint 3: Graph Performance Upgrade (April 28 \- May 9\)

- Generate synthetic data for HSL (Huge Soccer League)  
- Create vector db instance (swap out Neo4j)  
- Replatform functions to call from vector db, not neo4j  
- Refactor Zep personalization   
- Onboard F/E designer  
- Next demos:  
  - May 13  
  - May 20

#### Sprint 4: Integration and Polishing (May 12 \- May 23\)

- Testing / code freeze (except for fixes)  
- Stabilization and integration with marketing platforms team  
- F/E support  
- Next demo May 20

#### Sprint 5: INTERNAL Release Week (May 26 \- May 30\)

- Set up analytics tracking  
- Soft launch and stress testing  
- Go live  
- Capture feedback

## Question Backlog

- Scope of the project (e.g. what team / what dataset)  
- At what point does this become an Initiative that needs a team to take it across the finish line for deployment

