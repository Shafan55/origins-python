




using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Networking;
using UnityEngine.InputSystem;
using TMPro;

[Serializable] public class PieceData { public int row, col; public string type, owner, element, symbol; }
[Serializable] public class TileData  { public int row, col; public string type; }
[Serializable] public class MoveData  { public int from_row, from_col, to_row, to_col; }
[Serializable]
public class GameStateData {
    public int board_size; public string current_player, winner, difficulty;
    public bool game_over; public int steps, max_steps, valid_move_count;
    public PieceData[] pieces; public TileData[] tiles; public MoveData[] valid_moves;
}
[Serializable]
public class ApiResponse {
    public bool success, game_over, legal;
    public string error, message, result_message, winner, difficulty, reason;
    public float think_ms;
    public GameStateData game_state;
    public MoveData move;
}

public class OriginsGameManager : MonoBehaviour
{
    [Header("Server")]
    public string serverUrl = "http://127.0.0.1:5000";
    [Header("Custom Icons (optional)")]
    public Sprite iconMale, iconFemale, iconEarth, iconWater, iconFire, iconAir;

    GameObject[,] cells  = new GameObject[8,8];
    GameObject[,] pieces = new GameObject[8,8];
    List<GameObject> dots = new List<GameObject>();

    TextMeshProUGUI statusTMP, logTMP, infoTMP, serverDotTMP;
    Button btnEasy, btnNormal, btnHard;
    GameObject loadingPanel, gameOverPanel;
    TextMeshProUGUI gameOverTMP;
    Sprite circle;

    GameStateData state;
    int selRow=-1, selCol=-1;
    bool waiting=false;
    string difficulty="normal";
    List<string> logLines=new List<string>();

    const int SZ=8;
    const string P1="Player1", P2="Player2";
    const float CELL=58f, GAP=3f;

    static Color H(string h){ColorUtility.TryParseHtmlString("#"+h,out Color c);return c;}
    Color cBg=H("2b2416"),cPanel=H("1e1a12"),cNeutral=H("8a7e6a");
    Color cEarth=H("2d7a1a"),cWater=H("1a3d8a"),cFire=H("8a1a00"),cAir=H("3a3d50");
    Color cP1Out=H("555555"),cP1In=H("686868"),cP2Out=H("c85a00"),cP2In=H("a04000");
    Color cGold=H("e8c97e"),cSel=H("e8c97e"),cFlash=H("ff3333"),cGreen=H("2d8c2d");
    Color cDiffOn=H("5a4200"),cDiffOff=H("2e2820"),cStsBg=H("1a4a1a"),cDiv=H("3a3428");

    void Update(){if(Keyboard.current!=null&&Keyboard.current.escapeKey.wasPressedThisFrame)Application.Quit();}

    void Start()
    {
        circle=MakeCircle(128);
        if(Camera.main) Camera.main.backgroundColor=cBg;
        var cv0=FindFirstObjectByType<Canvas>();
        if(cv0){var cs=cv0.GetComponent<UnityEngine.UI.CanvasScaler>();if(cs){
            cs.uiScaleMode=UnityEngine.UI.CanvasScaler.ScaleMode.ScaleWithScreenSize;
            cs.referenceResolution=new Vector2(1366,768);
            cs.screenMatchMode=UnityEngine.UI.CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            cs.matchWidthOrHeight=0.5f;
        }}
        BuildUI();
        ShowLoading(false);
        ShowGameOver(false);
        RefreshDiffUI();
        SetOnline(false);
        if(statusTMP) statusTMP.text="Connecting...";
        StartCoroutine(Connect());
    }

    
    
    
    void BuildUI()
    {
        Canvas cv=FindFirstObjectByType<Canvas>();
        if(!cv)return;
        RectTransform root=cv.GetComponent<RectTransform>();

        
        var titleBar=MkRect("TitleBar",root);
        SetAnch(titleBar,0,1,1,1); SetOff(titleBar,0,-52,0,0);
        MkImg(titleBar,H("14110b"));

        var titleTxt=MkTMP("Title",titleBar,"OrOgins",30,TextAlignmentOptions.Center,cGold);
        SetAnch(titleTxt.rectTransform,0,0,1,1); SetOff(titleTxt.rectTransform,0,0,0,0);

        var srvBadge=MkRect("SrvBadge",titleBar);
        SetAnch(srvBadge,1,0,1,1); SetOff(srvBadge,-140,6,-10,-6);
        MkImg(srvBadge,H("0e1a0e"));
        serverDotTMP=MkTMP("SrvTxt",srvBadge,"● Offline",11,TextAlignmentOptions.Center,H("cc3333"));
        SetAnch(serverDotTMP.rectTransform,0,0,1,1); SetOff(serverDotTMP.rectTransform,4,2,-4,-2);

        
        var boardArea=MkRect("BoardArea",root);
        SetAnch(boardArea,0,0,0.58f,1); SetOff(boardArea,10,10,-10,-62);

        
        var bp=MkRect("BoardBg",boardArea);
        SetAnch(bp,0,0,1,1); SetOff(bp,24,24,-8,-8);
        MkImg(bp,H("25201a"));

        
        
        float step=CELL+GAP;
        float boardPx=SZ*step-GAP;
        var bg2=MkRect("CellArea",bp);
        bg2.sizeDelta=new Vector2(boardPx,boardPx);
        bg2.anchorMin=bg2.anchorMax=new Vector2(0.5f,0.5f);
        bg2.anchoredPosition=Vector2.zero;

        float start=-(SZ*step-GAP)/2f+CELL/2f;
        for(int r=0;r<SZ;r++) for(int c=0;c<SZ;c++)
        {
            var cell=MkRect($"Cell_{r}_{c}",bg2);
            cell.sizeDelta=new Vector2(CELL,CELL);
            cell.anchorMin=cell.anchorMax=new Vector2(0.5f,0.5f);
            cell.anchoredPosition=new Vector2(start+c*step,start+r*step);
            MkImg(cell,cNeutral);
            var btn=cell.gameObject.AddComponent<Button>();
            btn.transition=Selectable.Transition.None;
            int row=r,col=c;
            btn.onClick.AddListener(()=>OnClick(row,col));
            cells[r,c]=cell.gameObject;
        }
        
        for(int r=0;r<SZ;r++){
            var lbl=MkTMP($"RL{r}",bp,r.ToString(),11,TextAlignmentOptions.Right,H("998870"));
            lbl.rectTransform.sizeDelta=new Vector2(20,CELL);
            lbl.rectTransform.anchorMin=lbl.rectTransform.anchorMax=new Vector2(0.5f,0.5f);
            lbl.rectTransform.anchoredPosition=new Vector2(start-CELL/2f-14f,start+r*step);
        }
        
        for(int c=0;c<SZ;c++){
            var lbl=MkTMP($"CL{c}",bp,((char)('A'+c)).ToString(),11,TextAlignmentOptions.Center,H("998870"));
            lbl.rectTransform.sizeDelta=new Vector2(CELL,18);
            lbl.rectTransform.anchorMin=lbl.rectTransform.anchorMax=new Vector2(0.5f,0.5f);
            lbl.rectTransform.anchoredPosition=new Vector2(start+c*step,start-CELL/2f-16f);
        }

        
        var rp=MkRect("RightPanel",root);
        SetAnch(rp,0.58f,0,1,1); SetOff(rp,6,10,-10,-62);
        MkImg(rp,cPanel);

        
        var h1=MkRect("H1",rp); SetAnch(h1,0,1,1,1); SetOff(h1,10,-46,-10,-6);
        var h1t=MkTMP("T",h1,"OrOgins AI",22,TextAlignmentOptions.Center,cGold);
        FillRect(h1t.rectTransform);

        MkDiv(rp,52);

        
        var infoBox=MkRect("InfoBox",rp); SetAnch(infoBox,0,1,1,1); SetOff(infoBox,10,-96,-10,-58);
        MkImg(infoBox,H("2a2318"));
        infoTMP=MkTMP("T",infoBox,"DQN Agent • 8×8 Board\nConnected • AI vs Human",12,TextAlignmentOptions.Center,H("bbbbbb"));
        FillRect(infoTMP.rectTransform);

        MkDiv(rp,102);

        
        var dLbl=MkRect("DLbl",rp); SetAnch(dLbl,0,1,1,1); SetOff(dLbl,10,-120,-10,-106);
        MkTMP("T",dLbl,"Difficulty",13,TextAlignmentOptions.Left,H("999999")).rectTransform.Let(FillRect);

        
        var dRow=MkRect("DRow",rp); SetAnch(dRow,0,1,1,1); SetOff(dRow,10,-184,-10,-122);
        btnEasy  =MkDiffBtn(dRow,"EASY\nRandom",    0f,    0.31f);
        btnNormal=MkDiffBtn(dRow,"NORMAL\nBalanced",0.34f, 0.66f);
        btnHard  =MkDiffBtn(dRow,"HARD\nFull DQN",  0.69f, 1f);
        btnEasy.onClick.AddListener(()=>StartCoroutine(SetDiff("easy")));
        btnNormal.onClick.AddListener(()=>StartCoroutine(SetDiff("normal")));
        btnHard.onClick.AddListener(()=>StartCoroutine(SetDiff("hard")));

        MkDiv(rp,190);

        
        var sBox=MkRect("SBox",rp); SetAnch(sBox,0,1,1,1); SetOff(sBox,10,-260,-10,-196);
        MkImg(sBox,cStsBg);
        statusTMP=MkTMP("T",sBox,"●  Your turn — Player 1\nClick a grey piece to move\nNormal mode",13,TextAlignmentOptions.Left,Color.white);
        FillRect(statusTMP.rectTransform); statusTMP.margin=new Vector4(10,6,6,6);

        MkDiv(rp,260);

        
        var mLbl=MkRect("MLbl",rp); SetAnch(mLbl,0,1,1,1); SetOff(mLbl,10,-278,-10,-264);
        MkTMP("T",mLbl,"Move history",13,TextAlignmentOptions.Left,H("999999")).rectTransform.Let(FillRect);

        
        var logBox=MkRect("LogBox",rp); SetAnch(logBox,0,0,1,1); SetOff(logBox,10,150,-10,-282);
        MkImg(logBox,H("13100c"));
        logTMP=MkTMP("T",logBox,"",13,TextAlignmentOptions.TopLeft,H("dddddd"));
        logTMP.richText=true;
        logTMP.lineSpacing=4f;
        logTMP.overflowMode=TextOverflowModes.Truncate;
        FillRect(logTMP.rectTransform); logTMP.margin=new Vector4(8,8,8,8);

        
        MkDivFromBottom(rp,148);
        var legLbl=MkRect("LegLbl",rp); SetAnch(legLbl,0,0,1,0); SetOff(legLbl,10,130,-10,146);
        MkTMP("T",legLbl,"Tile legend",12,TextAlignmentOptions.Left,H("999999")).rectTransform.Let(FillRect);

        var legGrid=MkRect("LegGrid",rp); SetAnch(legGrid,0,0,1,0); SetOff(legGrid,10,68,-10,128);
        MkImg(legGrid,H("1a1610"));
        
        MkLegItem(legGrid,"<color=#2d9a2d>■</color> Earth",  0f,   0.32f, 1f, 0.5f);
        MkLegItem(legGrid,"<color=#2255cc>■</color> Water",  0.34f,0.65f, 1f, 0.5f);
        MkLegItem(legGrid,"<color=#cc2200>■</color> Fire",   0.67f,1f,    1f, 0.5f);
        
        MkLegItem(legGrid,"<color=#5a5a88>■</color> Air",    0f,   0.32f, 0.5f, 0f);
        MkLegItem(legGrid,"<color=#e8c97e>●</color> Valid move", 0.34f,1f,0.5f, 0f);

        MkDivFromBottom(rp,62);
        var bRow=MkRect("BRow",rp); SetAnch(bRow,0,0,1,0); SetOff(bRow,10,10,-10,58);
        var bNew=MkActionBtn(bRow,"New Game",cGreen,0f,0.58f);
        var bRec=MkActionBtn(bRow,"Reconnect",H("2a2520"),0.62f,1f);
        bNew.onClick.AddListener(()=>StartCoroutine(ResetGame()));
        bRec.onClick.AddListener(()=>StartCoroutine(Connect()));

        
        loadingPanel=MkRect("LoadPanel",root).gameObject;
        var lprt=loadingPanel.GetComponent<RectTransform>();
        SetAnch(lprt,0,0,1,1); SetOff(lprt,0,0,0,0);
        MkImg(lprt,new Color(0,0,0,0.55f));
        var lt=MkTMP("T",lprt,"AI is thinking...",22,TextAlignmentOptions.Center,Color.white);
        SetAnch(lt.rectTransform,0,0,1,1); SetOff(lt.rectTransform,0,0,0,0);

        
        gameOverPanel=MkRect("GOPanel",root).gameObject;
        var gort=gameOverPanel.GetComponent<RectTransform>();
        SetAnch(gort,0,0,1,1); SetOff(gort,0,0,0,0);
        MkImg(gort,new Color(0,0,0,0.72f));
        var goBox=MkRect("GoBox",gort);
        goBox.sizeDelta=new Vector2(360,160);
        goBox.anchorMin=goBox.anchorMax=new Vector2(0.5f,0.5f);
        goBox.anchoredPosition=Vector2.zero;
        MkImg(goBox,H("3a2e1a"));
        gameOverTMP=MkTMP("GT",goBox,"Game Over",22,TextAlignmentOptions.Center,cGold);
        SetAnch(gameOverTMP.rectTransform,0,1,1,1); SetOff(gameOverTMP.rectTransform,10,-90,-10,-10);
        var pa=MkActionBtn(goBox,"Play Again",cGreen,0f,1f);
        var part=pa.GetComponent<RectTransform>();
        SetAnch(part,0,0,1,0); SetOff(part,10,10,-10,54);
        pa.onClick.AddListener(()=>StartCoroutine(ResetGame()));
    }

    

    RectTransform MkRect(string name,RectTransform parent){
        var go=new GameObject(name); go.transform.SetParent(parent,false);
        return go.AddComponent<RectTransform>();
    }

    
    void SetAnch(RectTransform rt,float ax0,float ay0,float ax1,float ay1){
        rt.anchorMin=new Vector2(ax0,ay0); rt.anchorMax=new Vector2(ax1,ay1);
    }

    
    void SetOff(RectTransform rt,float l,float b,float r,float t){
        rt.offsetMin=new Vector2(l,b); rt.offsetMax=new Vector2(r,t);
    }

    void FillRect(RectTransform rt){
        rt.anchorMin=Vector2.zero; rt.anchorMax=Vector2.one;
        rt.offsetMin=rt.offsetMax=Vector2.zero;
    }

    Image MkImg(RectTransform rt,Color col){
        var img=rt.gameObject.GetComponent<Image>()??rt.gameObject.AddComponent<Image>();
        img.color=col; return img;
    }
    Image MkImg(GameObject go,Color col)=>MkImg(go.GetComponent<RectTransform>(),col);

    TextMeshProUGUI MkTMP(string name,RectTransform parent,string text,float size,TextAlignmentOptions align,Color col){
        var go=new GameObject(name); go.transform.SetParent(parent,false);
        var rt=go.AddComponent<RectTransform>();
        var tmp=go.AddComponent<TextMeshProUGUI>();
        tmp.text=text; tmp.fontSize=size; tmp.alignment=align; tmp.color=col;
        tmp.textWrappingMode=TextWrappingModes.Normal;
        return tmp;
    }

    void MkDiv(RectTransform parent,float fromTop){
        var d=MkRect("Div",parent);
        SetAnch(d,0,1,1,1); SetOff(d,8,-(fromTop+1),-8,-fromTop);
        MkImg(d,cDiv);
    }

    void MkDivFromBottom(RectTransform parent,float fromBottom){
        var d=MkRect("DivB",parent);
        SetAnch(d,0,0,1,0); SetOff(d,8,fromBottom,-8,fromBottom+1);
        MkImg(d,cDiv);
    }

    Button MkDiffBtn(RectTransform parent,string label,float x0,float x1){
        var rt=MkRect("DB",parent);
        SetAnch(rt,x0,0,x1,1); SetOff(rt,2,0,-2,0);
        MkImg(rt,cDiffOff);
        var tmp=MkTMP("T",rt,label,12,TextAlignmentOptions.Center,H("888888"));
        FillRect(tmp.rectTransform); tmp.margin=new Vector4(3,6,3,4);
        var btn=rt.gameObject.AddComponent<Button>(); btn.transition=Selectable.Transition.None;
        return btn;
    }

    Button MkActionBtn(RectTransform parent,string label,Color bg,float x0,float x1){
        var rt=MkRect("AB",parent);
        SetAnch(rt,x0,0,x1,1); SetOff(rt,2,0,-2,0);
        MkImg(rt,bg);
        var tmp=MkTMP("T",rt,label,13,TextAlignmentOptions.Center,Color.white);
        FillRect(tmp.rectTransform);
        var btn=rt.gameObject.AddComponent<Button>(); btn.transition=Selectable.Transition.None;
        return btn;
    }

    void MkLegItem(RectTransform parent,string label,float x0,float x1,float y1,float y0){
        var rt=MkRect("LI",parent);
        SetAnch(rt,x0,y0,x1,y1); SetOff(rt,4,2,-4,-2);
        
        var sq=MkRect("Sq",rt);
        sq.anchorMin=new Vector2(0,0.5f); sq.anchorMax=new Vector2(0,0.5f);
        sq.sizeDelta=new Vector2(13,13); sq.anchoredPosition=new Vector2(8,0);
        
        Color sqCol=Color.white;
        int ci=label.IndexOf("<color=#");
        if(ci>=0){string hex=label.Substring(ci+8,6);ColorUtility.TryParseHtmlString("#"+hex,out sqCol);}
        MkImg(sq,sqCol);
        
        int end=label.IndexOf("</color>");
        string txt=end>=0?label.Substring(end+8).Trim():label;
        var tmp=MkTMP("T",rt,txt,13,TextAlignmentOptions.Left,H("cccccc"));
        tmp.enableWordWrapping=false;
        FillRect(tmp.rectTransform); tmp.margin=new Vector4(26,0,0,0);
    }

    
    
    
    IEnumerator Connect(){
        SetOnline(false);
        if(statusTMP)statusTMP.text="Connecting...";
        using var req=UnityWebRequest.Get($"{serverUrl}/health");
        req.timeout=5; yield return req.SendWebRequest();
        if(req.result==UnityWebRequest.Result.Success){
            SetOnline(true);
            if(infoTMP)infoTMP.text="DQN Agent • 8x8 Board\nConnected • AI vs Human";
            yield return StartCoroutine(ResetGame());
        } else {
            if(statusTMP)statusTMP.text="Cannot connect.\nRun ai_flask_server.py first.";
        }
    }

    IEnumerator ResetGame(){
        ShowLoading(true); ShowGameOver(false); ClearAll();
        yield return Post("/reset","{\"board_size\":8}",r=>{
            if(r.success&&r.game_state!=null){
                state=r.game_state; DrawBoard();
                if(statusTMP)statusTMP.text=$"●  Your turn — Player 1\nClick a grey piece to move\n{Cap(difficulty)} mode";
                Log($"Game started — {Cap(difficulty)} mode",false);
            }
        });
        ShowLoading(false);
    }

    IEnumerator SetDiff(string d){
        yield return Post("/difficulty",$"{{\"difficulty\":\"{d}\"}}",r=>{
            if(r.success){difficulty=d;RefreshDiffUI();Log($"Difficulty: {Cap(d)}",false);}
        });
    }

    IEnumerator DoMove(int fr,int fc,int tr,int tc){
        waiting=true; ShowLoading(true);
        if(statusTMP)statusTMP.text="AI is thinking...";
        string body=$"{{\"human_move\":{{\"from_row\":{fr},\"from_col\":{fc},\"to_row\":{tr},\"to_col\":{tc}}}}}";
        yield return Post("/move",body,r=>{
            if(!r.success){StartCoroutine(Flash(tr,tc));if(statusTMP)statusTMP.text="Invalid move";return;}
            Log($"You: {fr}{CL(fc)} -> {tr}{CL(tc)}",false);
            if(r.move!=null)Log($"AI: {r.move.from_row}{CL(r.move.from_col)} -> {r.move.to_row}{CL(r.move.to_col)} [{r.think_ms:F0}ms]",true);
            if(r.game_state!=null){state=r.game_state;DrawBoard();}
            if(r.game_over)GameOver(r.winner);
            else if(statusTMP)statusTMP.text=$"●  Your turn — Player 1\nClick a grey piece to move\n{Cap(difficulty)} mode";
        });
        ShowLoading(false); waiting=false;
    }

    IEnumerator Post(string ep,string json,Action<ApiResponse> cb){
        byte[] b=System.Text.Encoding.UTF8.GetBytes(json);
        using var req=new UnityWebRequest($"{serverUrl}{ep}","POST");
        req.uploadHandler=new UploadHandlerRaw(b);
        req.downloadHandler=new DownloadHandlerBuffer();
        req.SetRequestHeader("Content-Type","application/json");
        req.timeout=15; yield return req.SendWebRequest();
        if(req.result==UnityWebRequest.Result.Success)
            cb?.Invoke(JsonUtility.FromJson<ApiResponse>(req.downloadHandler.text));
        else Debug.LogError($"[Origins] {ep}: {req.error}");
    }

    
    
    
    void DrawBoard(){
        if(state==null)return;
        for(int r=0;r<SZ;r++)for(int c=0;c<SZ;c++)SetCell(r,c,cNeutral);
        if(state.tiles!=null)foreach(var t in state.tiles)
            if(InB(t.row,t.col) && t.row != 0 && t.row != 7)
                SetCell(t.row,t.col,TileCol(t.type));
        ClearPieces();
        if(state.pieces!=null)foreach(var p in state.pieces){
            if(!InB(p.row,p.col)||cells[p.row,p.col]==null)continue;
            var obj=BuildPiece(p);
            obj.transform.SetParent(cells[p.row,p.col].transform,false);
            var rt=obj.GetComponent<RectTransform>();
            rt.anchoredPosition=Vector2.zero;
            rt.sizeDelta=new Vector2(CELL-6f,CELL-6f);
            pieces[p.row,p.col]=obj;
        }
    }

    void SetCell(int r,int c,Color col){if(cells[r,c])cells[r,c].GetComponent<Image>().color=col;}
    Color TileCol(string t)=>t switch{"tile_earth"=>cEarth,"tile_water"=>cWater,"tile_fire"=>cFire,"tile_air"=>cAir,_=>cNeutral};

    void ClearPieces(){
        for(int r=0;r<SZ;r++)for(int c=0;c<SZ;c++)
            if(pieces[r,c]){Destroy(pieces[r,c]);pieces[r,c]=null;}
    }

    GameObject BuildPiece(PieceData p){
        bool p1=p.owner==P1;
        var outer=new GameObject("Piece"); outer.AddComponent<RectTransform>();
        var oi=outer.AddComponent<Image>(); oi.sprite=circle; oi.color=p1?cP1Out:cP2Out;
        var inner=new GameObject("In"); inner.transform.SetParent(outer.transform,false);
        var ir=inner.AddComponent<RectTransform>();
        ir.anchorMin=ir.anchorMax=new Vector2(0.5f,0.5f);
        ir.sizeDelta=Vector2.one*(CELL-6f)*0.70f; ir.anchoredPosition=Vector2.zero;
        var ii=inner.AddComponent<Image>(); ii.sprite=circle; ii.color=p1?cP1In:cP2In;
        Sprite spr=GetSpr(p);
        if(spr!=null){
            var ic=new GameObject("Ic"); ic.transform.SetParent(outer.transform,false);
            var irt=ic.AddComponent<RectTransform>(); irt.anchorMin=Vector2.zero; irt.anchorMax=Vector2.one; irt.offsetMin=irt.offsetMax=Vector2.zero;
            var img=ic.AddComponent<Image>(); img.sprite=spr; img.preserveAspect=true;
        } else {
            var tc=new GameObject("Lb"); tc.transform.SetParent(outer.transform,false);
            var trt=tc.AddComponent<RectTransform>(); trt.anchorMin=Vector2.zero; trt.anchorMax=Vector2.one; trt.offsetMin=trt.offsetMax=Vector2.zero;
            var tmp=tc.AddComponent<TextMeshProUGUI>();
            tmp.text=PieceLbl(p); tmp.fontSize=CELL*0.32f; tmp.alignment=TextAlignmentOptions.Center; tmp.color=Color.white;
        }
        return outer;
    }

    Sprite GetSpr(PieceData p){
        if(p.type=="male")return iconMale; if(p.type=="female")return iconFemale;
        if(p.element=="earth")return iconEarth; if(p.element=="water")return iconWater;
        if(p.element=="fire")return iconFire; if(p.element=="air")return iconAir;
        return null;
    }

    string PieceLbl(PieceData p){
        if(p.type=="male")return"M"; if(p.type=="female")return"F";
        return p.element switch{"earth"=>"Ea","water"=>"Wa","fire"=>"Fi","air"=>"Ai",_=>"?"};
    }

    void ShowDots(int fr,int fc){
        ClearDots();
        if(state?.valid_moves==null)return;
        foreach(var vm in state.valid_moves){
            if(vm.from_row!=fr||vm.from_col!=fc)continue;
            if(!InB(vm.to_row,vm.to_col)||cells[vm.to_row,vm.to_col]==null)continue;
            var dot=new GameObject("Dot"); dot.transform.SetParent(cells[vm.to_row,vm.to_col].transform,false);
            var rt=dot.AddComponent<RectTransform>(); rt.anchorMin=rt.anchorMax=new Vector2(0.5f,0.5f);
            rt.sizeDelta=Vector2.one*CELL*0.28f; rt.anchoredPosition=Vector2.zero;
            var img=dot.AddComponent<Image>(); img.sprite=circle; img.color=cGold;
            dots.Add(dot);
        }
    }

    void ClearDots(){foreach(var d in dots)if(d)Destroy(d);dots.Clear();}

    IEnumerator Flash(int r,int c){
        if(!InB(r,c)||cells[r,c]==null)yield break;
        var img=cells[r,c].GetComponent<Image>(); if(!img)yield break;
        var orig=img.color;
        for(int i=0;i<3;i++){img.color=cFlash;yield return new WaitForSeconds(0.08f);img.color=orig;yield return new WaitForSeconds(0.08f);}
    }

    void ClearSel(){
        if(InB(selRow,selCol)&&pieces[selRow,selCol])
            pieces[selRow,selCol].GetComponent<Image>().color=state?.current_player==P1?cP1Out:cP2Out;
        selRow=selCol=-1; ClearDots();
    }

    void Select(int r,int c){
        selRow=r; selCol=c;
        if(pieces[r,c])pieces[r,c].GetComponent<Image>().color=cSel;
        ShowDots(r,c);
    }

    void OnClick(int r,int c){
        if(waiting||state==null||state.game_over)return;
        if(state.current_player!=P1)return;
        if(selRow==-1){
            bool has=false;
            if(state.pieces!=null)foreach(var p in state.pieces)if(p.row==r&&p.col==c&&p.owner==P1){has=true;break;}
            if(!has){StartCoroutine(Flash(r,c));if(statusTMP)statusTMP.text="No piece there!\nPick a grey piece";return;}
            ClearSel(); Select(r,c);
        } else {
            if(r==selRow&&c==selCol){ClearSel();if(statusTMP)statusTMP.text="Your turn\nClick a grey piece";return;}
            bool own=false;
            if(state.pieces!=null)foreach(var p in state.pieces)if(p.row==r&&p.col==c&&p.owner==P1){own=true;break;}
            if(own){ClearSel();Select(r,c);return;}
            bool valid=false;
            if(state.valid_moves!=null)foreach(var vm in state.valid_moves)
                if(vm.from_row==selRow&&vm.from_col==selCol&&vm.to_row==r&&vm.to_col==c){valid=true;break;}
            int fr=selRow,fc=selCol; ClearSel();
            if(!valid){StartCoroutine(Flash(r,c));if(statusTMP)statusTMP.text="Not a legal move!";return;}
            StartCoroutine(DoMove(fr,fc,r,c));
        }
    }

    void RefreshDiffUI(){
        SetDiffBtn(btnEasy,difficulty=="easy");
        SetDiffBtn(btnNormal,difficulty=="normal");
        SetDiffBtn(btnHard,difficulty=="hard");
    }

    void SetDiffBtn(Button btn,bool on){
        if(!btn)return;
        btn.GetComponent<Image>().color=on?cDiffOn:cDiffOff;
        var tmp=btn.GetComponentInChildren<TextMeshProUGUI>();
        if(tmp)tmp.color=on?cGold:H("888888");
    }

    void GameOver(string winner){
        ShowGameOver(true);
        string msg=winner==P1?"You Win!\nPieces reached the goal!":winner==P2?$"AI Wins!\n{Cap(difficulty)} mode":"Draw!";
        if(gameOverTMP)gameOverTMP.text=msg;
        if(statusTMP)statusTMP.text="Game Over!";
        Log($"-- {winner??"Draw"} wins --",winner==P2);
    }

    void ClearAll(){ClearSel();ClearPieces();ClearDots();logLines.Clear();if(logTMP)logTMP.text="";}
    void ShowLoading(bool v){if(loadingPanel)loadingPanel.SetActive(v);}
    void ShowGameOver(bool v){if(gameOverPanel)gameOverPanel.SetActive(v);}

    void SetOnline(bool v){
        if(!serverDotTMP)return;
        serverDotTMP.text=v?"● Online":"● Offline";
        serverDotTMP.color=v?H("33cc55"):H("cc3333");
    }

    void Log(string msg,bool isAI){
        string dc=isAI?"#c05010":"#888888",tc=isAI?"#dddddd":"#aaaaaa";
        logLines.Add($"<color={dc}>●</color> <color={tc}>{msg}</color>");
        if(logLines.Count>6)logLines.RemoveAt(0);
        if(logTMP)logTMP.text=string.Join("\n",logLines);
    }

    Sprite MakeCircle(int size){
        float r=size/2f;
        var tx=new Texture2D(size,size,TextureFormat.RGBA32,false);
        tx.filterMode=FilterMode.Bilinear;
        var px=new Color[size*size];
        var ct=new Vector2(r-0.5f,r-0.5f);
        for(int y=0;y<size;y++) for(int x=0;x<size;x++){
            float dist=Vector2.Distance(new Vector2(x,y),ct);
            float alpha=Mathf.Clamp01(r-0.5f-dist+1f); 
            px[y*size+x]=new Color(1,1,1,alpha);
        }
        tx.SetPixels(px); tx.Apply();
        return Sprite.Create(tx,new Rect(0,0,size,size),new Vector2(0.5f,0.5f),100f,1,SpriteMeshType.FullRect);
    }

    bool InB(int r,int c)=>r>=0&&r<SZ&&c>=0&&c<SZ;
    string CL(int col)=>((char)('A'+col)).ToString();
    string Cap(string d)=>d switch{"easy"=>"Easy","normal"=>"Normal","hard"=>"Hard",_=>d};
}


public static class RectTransformExt {
    public static void Let(this RectTransform rt, Action<RectTransform> action) => action(rt);
}
