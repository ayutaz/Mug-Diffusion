import matplotlib.pyplot as plt
import numpy as np
from scipy import optimize
import cvxpy as cp

data = {
    'gbc_rice': [1.0, 0.9989611017803157, 0.9987294591871011, 0.9969397379912663, 0.9960674504534767, 0.9953913335572724, 0.9950994961370506, 0.9936177359758145, 0.9932872018810883, 0.9926035606315081, 0.9919118575747397, 0.9913233456499831, 0.9911873698354047, 0.98892791400739, 0.9888967416862613, 0.987918038293584, 0.9861600268726906, 0.9858042324487739, 0.9855801142089351, 0.9852237823312059, 0.9836549546523345, 0.9829396036278132, 0.9815862949277796, 0.9811686933154181, 0.9804694659052737, 0.9802609338259992, 0.9786383607658715, 0.9780632851864293, 0.9776134363453141, 0.9755420893516964, 0.9753362445414846, 0.9748305005038629, 0.9735239502855222, 0.973516963385959, 0.9733455156197514, 0.9731531071548537, 0.97006973463218, 0.9685492777964394, 0.9660732280819616, 0.9651805172992945, 0.963622976150487, 0.9636154517971112, 0.9627485387974469, 0.9626534094726233, 0.9622879408800805, 0.9619208599261001, 0.9609152838427947, 0.957252536110178, 0.9570633523681558, 0.9567113201209271, 0.9563458515283841, 0.9542675176352031, 0.9536295599596909, 0.9533441719852199, 0.9498899563318776, 0.948377023849513, 0.9479459858918373, 0.9475283842794759, 0.9465335572724218, 0.945165737319449, 0.9451431642593213, 0.9444939200537453, 0.9416916358750419, 0.9401228081961706, 0.9394047699025864, 0.9330746388982195, 0.9329795095733959, 0.9318954652334565, 0.9288824991602282, 0.9281800470272086, 0.9271680214981525, 0.9261097749412159, 0.9247999999999998, 0.9246704736311723, 0.9245135371179038, 0.9240163923412831, 0.9153306012764527, 0.9128636882767885, 0.9121703728585824, 0.9108036278132348, 0.9106413167618408, 0.9096373530399731, 0.9067759489418877, 0.904499294591871, 0.8948337252267383, 0.8935110513940208, 0.8909081625797782, 0.8891689620423244, 0.8847113201209271, 0.8846860597917365, 0.8813608330534095, 0.8803149479341618, 0.8789095062143096, 0.8760545515619752, 0.8747920725562647, 0.8732753778972119, 0.8712008061807188, 0.8704988915015115, 0.8604399059455827, 0.8531547195162914, 0.8487244877393348, 0.8470621430970775, 0.8450466912999663, 0.8388826335236815, 0.8358266711454483, 0.8343180382935841, 0.8335064830366139, 0.8067858918374202, 0.8065375881760162, 0.8045253611017803, 0.7785314074571715, 0.7563453140745716, 0.7432083305340946, 0.6566487067517635, 0.6279271750083976, 0.5417201209271079, 0.534673026536782, 0.5168542828350688, 0.43977964393684915, 0.3849770910312395, 0.31438468256634194, 0.3082442727578098, 0.19595673496808866, 0.057677393349009065, 0.0],
    'gbc_ln': [1.0, 0.9958008723459488, 0.9918399424902082, 0.990927088652371, 0.9890043902564264, 0.986388493477374, 0.9855797620304152, 0.9854257179452801, 0.9844329893966322, 0.9820438797429175, 0.9781285925790688, 0.9752245763074492, 0.9747353437037333, 0.9734231163118423, 0.9730337270966398, 0.9721864846283972, 0.9694308071054261, 0.9619853429905663, 0.9616672704814448, 0.9613220976240127, 0.9609113133969859, 0.9576963562868529, 0.9571072802946236, 0.9542788597314498, 0.9513634327868572, 0.9511765830169249, 0.9511523353368573, 0.9503835412453038, 0.9498800453003717, 0.9498030232578042, 0.9492210789361829, 0.9471314994480087, 0.9464596960767253, 0.9428910081044305, 0.9415459750277422, 0.9403521333679457, 0.9385806263888928, 0.9385093096828118, 0.9324416843294375, 0.9316771692402489, 0.931454661117276, 0.930574612964236, 0.929947025950723, 0.9277633084105218, 0.9221307149642418, 0.9132389480500587, 0.9092951342037775, 0.9083238006669538, 0.9079971701531027, 0.9078802107551298, 0.903100565113579, 0.9008027408436481, 0.8951715737314897, 0.8931076682575046, 0.8930063985348696, 0.8905459721750739, 0.8879158120548054, 0.8856935834933205, 0.8852499935814965, 0.8841445846372404, 0.8824386890277821, 0.8767604528896102, 0.8746879894108954, 0.8740275967125851, 0.8724286761622484, 0.8643741673774565, 0.863913461456173, 0.8629421279193493, 0.8621177067970526, 0.8582666046686769, 0.856329642931516, 0.8560928714673269, 0.8560572131142864, 0.8398440731538245, 0.8379998231345689, 0.8310364599528168, 0.8307996884886278, 0.8284219895078861, 0.8185189517014739, 0.809765539197088, 0.8076103483393192, 0.8035695437727679, 0.7990551962778385, 0.7989425158822304, 0.7959985622552054, 0.7936993116511529, 0.7887142738960887, 0.7780937900265013, 0.7749872343096115, 0.7740358694504905, 0.7583319307714471, 0.7473990797292247, 0.743886018787673, 0.742904700911998, 0.7397211231525407, 0.7395499630579463, 0.7326907222670725, 0.720987650799175, 0.7137418734613421, 0.70951564545898, 0.7020302439887148, 0.6894428453654126, 0.6815994340306205, 0.6655859808471855, 0.6622455063343499, 0.6295410912597098, 0.5994140619428382, 0.5673258232087383, 0.5415091756074044, 0.520059963086473, 0.5124504705476267, 0.5034046595483085, 0.47235621838887004, 0.44284679174666025, 0.44049761944835103, 0.42633982695714434, 0.4119324259946541, 0.39625558766392144, 0.3647721145973887, 0.33638663924301593, 0.32246704455011993, 0.3049231348541859, 0.2445934805119969, 0.16696809861103584, 0.0],
    'gbc_hb': [1.0, 0.9954554960915044, 0.9914515234393549, 0.9896147275065748, 0.9890741962502286, 0.988914562720317, 0.9862755577827913, 0.9825666040593393, 0.9818745219834567, 0.9817017540491854, 0.9815693996667902, 0.9814996862898036, 0.9811945639731371, 0.9807207150773869, 0.9798073688049814, 0.9787495440846179, 0.975049683410338, 0.9744879350392567, 0.9726279013141477, 0.9710113592390937, 0.9686411044215457, 0.9672710850129373, 0.9661708260631038, 0.9634974696064832, 0.961538422679277, 0.9609898087125556, 0.9606008282757457, 0.9604361430518495, 0.9602148788553265, 0.9601946720793884, 0.9592055503972147, 0.9584558790099084, 0.9582002632942904, 0.9578698825077013, 0.9567574994923047, 0.9512107394972756, 0.9508278210932471, 0.9500963358042852, 0.9499164954984355, 0.9493486850945727, 0.9483868425599156, 0.9453992707374564, 0.945226502803185, 0.9431462152203498, 0.9422439826747103, 0.942081318128408, 0.9375105454111927, 0.9362799527565578, 0.9362152910735557, 0.9351968695662717, 0.9341794583977845, 0.9341693550098155, 0.9333358255023657, 0.9271788208740037, 0.9227777850746691, 0.9222049229768218, 0.9209137099943724, 0.920088263197298, 0.9193062609684906, 0.9190304384769344, 0.9182969325103787, 0.9179160347839441, 0.9177998458222996, 0.9139999616071257, 0.903864242796537, 0.8980618670858899, 0.8945408363786629, 0.892489848620938, 0.8874765475106767, 0.8873664205818137, 0.8842535667485378, 0.8837716351424123, 0.8824733497883845, 0.878414818841202, 0.8777752743827588, 0.8774721727436862, 0.8713080957437458, 0.8699057454936364, 0.8692257874833168, 0.8689176341502596, 0.867240471747391, 0.8656956637269175, 0.8655875574756483, 0.8613522172390068, 0.8495160982332205, 0.8400512443837792, 0.8363604767586715, 0.8324322795162902, 0.8189119257360571, 0.816919537628553, 0.8154232258703311, 0.8098764658753019, 0.8083983402154244, 0.8000701175125055, 0.7926410963388353, 0.7901900144175347, 0.7868043691090933, 0.7852080338099775, 0.7827296727411603, 0.7807443570052346, 0.7730354719848207, 0.7717664864559033, 0.7669562634438206, 0.7563042615080114, 0.7435123620003495, 0.7101560266204067, 0.684005427540017, 0.6661608237090143, 0.6205349339794113, 0.6123522000632472, 0.5939771683638675, 0.5701857103742598, 0.5415042126076137, 0.5172267816566929, 0.5007511868955017, 0.4956014900476577, 0.4924128608046136, 0.4172446646533982, 0.3954678222248266, 0.37256142102131107, 0.37211080991788975, 0.36533345726822575, 0.11143127624986486, 0.04682617222033064, 0.0],
    'mcnc_rice': [1.0, 0.9972761885385382, 0.9939333856147256, 0.9914512525339213, 0.9843649042658659, 0.983193505023453, 0.9821417120429696, 0.982078826406049, 0.9790936082298805, 0.9768901447109485, 0.9699949195803682, 0.9690849274225771, 0.9658198067561369, 0.9643179497802702, 0.9641749156592636, 0.9637038900315168, 0.9600922813429417, 0.9547778287439149, 0.9531354038737553, 0.9520268902682629, 0.9488382185608809, 0.9484325444268533, 0.9479035652456983, 0.9387826820354231, 0.9367678754272526, 0.9357234807569951, 0.9319232151576584, 0.9291414505127034, 0.9181919513783056, 0.8955925798647592, 0.8881264519183818, 0.8875888411286866, 0.877107901765237, 0.8715653344776053, 0.8673581618158417, 0.8630646760279952, 0.840740274921208, 0.8262210911027921, 0.8259078958465889, 0.8197993578266723, 0.8158807192637206, 0.7978436389328681, 0.7843725493097377, 0.7838226081263041, 0.7826105181776486, 0.7716696506517912, 0.7381540720299488, 0.7088210052823934, 0.5894702314191443, 0.5787365165796132, 0.4614720662000803, 0.4321673593951146, 0.3093566429427519, 0.0],
    'mcnc_ln': [1.0, 0.9709931715982901, 0.9700109749796088, 0.9690437248312116, 0.9685013814808963, 0.9637889729212663, 0.9623840047145438, 0.9618779599349188, 0.9590658883114332, 0.9581178550534016, 0.9511100957001141, 0.9481506945838262, 0.9474033710696121, 0.9462311407573163, 0.93870452536416, 0.9378504413479154, 0.9340348210053423, 0.9293587110164027, 0.9147261166080908, 0.9142307478786689, 0.9114485691957518, 0.8972793153662526, 0.8972152590650342, 0.8971277154533691, 0.8954836037220981, 0.8953426798594177, 0.894247317108584, 0.8914630032156263, 0.885943485260645, 0.8782652699546054, 0.8625202311151348, 0.8590419739589783, 0.8352749509969296, 0.834948263860716, 0.8219896741242436, 0.7990489774479116, 0.7835494877631113, 0.7775004377180583, 0.7471697790911692, 0.7443876004082521, 0.7415392302140762, 0.7107495014284555, 0.7058577352254142, 0.7025396188223035, 0.701706886906465, 0.6850095443888815, 0.6760480678484343, 0.6659164962057318, 0.6544269309772002, 0.6378961348427845, 0.6077448338593068, 0.5088760681388228, 0.03894836635079793, 0.0],
    'mcnc_hb': [1.0, 0.9965360788579709, 0.9959514508171221, 0.9885726097586948, 0.9811311299816051, 0.9803042988952618, 0.974629230984451, 0.9680459016530358, 0.9601325435286896, 0.9468781906597319, 0.94596575332455, 0.9458634434174015, 0.9445563821546467, 0.9444519842902094, 0.9428338173914315, 0.9345759463144422, 0.9256039938447019, 0.9115541292487321, 0.9113286298615475, 0.905684881310068, 0.9027867965932889, 0.8980784529071674, 0.8961095091838801, 0.8938127561662599, 0.8869287609852653, 0.879048810177539, 0.8771090978562942, 0.8707617076985074, 0.8647922378099834, 0.8592173918490323, 0.8448125745139757, 0.7882936586649183, 0.77836959767151, 0.7633676245518721, 0.7614487918035149, 0.7546796342734013, 0.7545105097330129, 0.7489711590459706, 0.7423982695009991, 0.7336476405038659, 0.7217254043851279, 0.6901074671616517, 0.6842820663260513, 0.6784441377467183, 0.6346367058715446, 0.6330227148873443, 0.6247418762801789, 0.598565155751174, 0.5760381845628966, 0.5491995815733594, 0.5450633381843542, 0.38618858012640495, 0.026907505580065855, 0.0],
    'mwc': [1.0, 0.9780286074001538, 0.9761925578792754, 0.9702239397542608, 0.9681372549019608, 0.9665693268984169, 0.9642116061644634, 0.9622910400783381, 0.9529679886223217, 0.9508026159334126, 0.9390927001002541, 0.9328268168147164, 0.9322177146720757, 0.922900491944697, 0.9217464036744305, 0.9131752582126786, 0.911362523606351, 0.893663589097946, 0.8912126087057891, 0.8896563381595206, 0.8539262316103612, 0.8510264391131006, 0.842149285397869, 0.8410826280571682, 0.7613310484717074, 0.7513610081369052, 0.7288446294094332, 0.7163361777529086, 0.7038073255461519, 0.6732385582056841, 0.6652881723438484, 0.583120584738057, 0.5685604206010585, 0.5603681425007577, 0.5256668065561539, 0.5215371523163368, 0.4662283462731109, 0.4618946865309739, 0.37231004173369703, 0.1368818633279709, 0.0]
}

# def fit(x, a, t=True):
#     if t:
#         a = a ** 2 + 1
#     return (a * (x - 1)) / (x - a)
#
for k, d in data.items():
    x = np.linspace(0, 1, len(d))
    # a = optimize.curve_fit(fit, x, d)[0]
    # new_y = fit(x, a)
    # print(f"Fit: {k} - {a ** 2 + 1}")
    plt.plot(x, d, label=k, linestyle=':')
#

N = 120 # player count
x = np.linspace(0, 1, N)
a = 1.1
scores = a * (x - 1) / (x - a)

# N = len(data['mwc']) # player count
NUM_PER_TEAM = 5
M = N // NUM_PER_TEAM # team count
N = N - M
NUM_PER_TEAM -= 1

# plt.plot(x, scores, label="fit", linewidth=3)
# plt.legend()
# plt.show()
plt.clf()
# scores = a * (x - 1) / (x - a)
scores = scores[:N]
# scores = 1 - x
mean_scores_per_team = np.sum(scores) / M

import gurobipy as gp
from gurobipy import GRB

var = cp.Variable((M, N), integer=True)
epsilon = cp.Variable()

constraints = [0 <= var, var <= 1, epsilon >= 0.006]
# 1.05: 0.009
# 1.1: 0.006
for player_idx in range(N):
    constraints.append(sum((var[team_idx, player_idx] for team_idx in range(M))) == 1)
for team_idx in range(M):
    constraints.append(sum((var[team_idx, player_idx] for player_idx in range(N))) == NUM_PER_TEAM)
print(len(constraints))


for team_idx in range(M):
    diff = (sum(var[team_idx, player_idx] * scores[player_idx] for player_idx in range(N)) - mean_scores_per_team)
    constraints.append(diff <= epsilon)
    constraints.append(diff >= -epsilon)

objective = cp.Minimize(epsilon)

prob = cp.Problem(objective, constraints)
result = prob.solve(solver=cp.GLPK_MI, verbose=True)
print(objective.value)

# var = model.addVars(M, N, vtype=GRB.BINARY)
# model.addConstrs((
#     gp.quicksum(var[team_idx, player_idx] for team_idx in range(M)) == 1
#     for player_idx in range(N)
# ), name = 'player')
# model.addConstrs((
#     gp.quicksum(var[team_idx, player_idx] for player_idx in range(N)) == NUM_PER_TEAM
#     for team_idx in range(M)
# ), name = 'team')
# model.setObjective(
#     gp.quicksum(
#         (gp.quicksum(var[team_idx, player_idx] * scores[player_idx] for player_idx in range(N)) - mean_scores_per_team) ** 2
#         for team_idx in range(M)
#     )
# )
# model.optimize()
#

for a in [1.1, 1.05, 1.08, 1.1, 1.13, 1.15]:
    N = 120 # player count
    x = np.linspace(0, 1, N)
    scores = a * (x - 1) / (x - a)

    # N = len(data['mwc']) # player count
    NUM_PER_TEAM = 5
    M = N // NUM_PER_TEAM # team count
    N = N - M
    NUM_PER_TEAM -= 1

    # plt.plot(x, scores, label="fit", linewidth=3)
    # plt.legend()
    # plt.show()

    # scores = a * (x - 1) / (x - a)
    scores = scores[:N]
    # scores = 1 - x
    mean_scores_per_team = np.sum(scores) / M

    print(mean_scores_per_team)
    value = var.value
    error = 0
    team_dict = {}
    result = []
    team_scores = []
    for i in range(M):
        cur_s = 0
        for j in range(N):
            # print(value[i, j], ' ', end='')
            cur_s += value[i, j] * scores[j]
        team_scores.append(cur_s)
        error += abs(mean_scores_per_team - cur_s)
        # print(cur_s)
    print(f"Error: {error} (a = {a})")
    team_scores = sorted(team_scores)
    # plt.clf()
    plt.plot(np.arange(1, len(team_scores) + 1), team_scores, label="IP", marker="o", markersize=5)

    # snake
    value_snake = np.zeros_like(value)
    order = True
    cur_team = 0
    team_scores = []
    for i in range(N):
        value_snake[cur_team, i] = 1.0
        if order:
            if cur_team == M - 1:
                order = False
            else:
                cur_team += 1
        else:
            if cur_team == 0:
                order = True
            else:
                cur_team -= 1

    # print(mean_scores_per_team)
    snake_error = 0
    # team_scores = []
    for i in range(M):
        cur_s = 0
        for j in range(N):
            cur_s += value_snake[i, j] * scores[j]
        team_scores.append(cur_s)
        snake_error += abs(mean_scores_per_team - cur_s)
    print(f"Snake Error: {snake_error}")
    print(f"Reduce: {1 - (error) / snake_error}")
    plt.plot(np.arange(1, len(team_scores) + 1), team_scores, label="Snake", marker="o",
             markersize=5)

    # Naive
    value_snake = np.zeros_like(value)
    order = True
    cur_team = 0
    team_scores = []
    for i in range(N):
        value_snake[cur_team, i] = 1.0
        if cur_team == M - 1:
            cur_team = 0
        else:
            cur_team += 1

    # print(mean_scores_per_team)
    naive_error = 0
    # team_scores = []
    for i in range(M):
        cur_s = 0
        for j in range(N):
            cur_s += value_snake[i, j] * scores[j]
        team_scores.append(cur_s)
        naive_error += abs(mean_scores_per_team - cur_s)
    print(f"Naive Error: {naive_error}")
    team_scores = sorted(team_scores)
    print(f"Reduce: {1 - (error) / naive_error}")

    team_dict = {}
    result = []
    for j in range(N):
        for i in range(M):
            if value_snake[i, j] == 1:
                if i not in team_dict:
                    team_dict[i] = len(team_dict) + 1
                result.append(str(team_dict[i]))
                break
    print(" -> ".join(result))


    # plt.plot(np.arange(1, len(team_scores) + 1), team_scores, label="Order", marker="o", markersize=5)
    # plt.xlabel("Team")
    # plt.ylabel("Team score")
    # plt.legend()
    # plt.show()
# print(f"Error: {error}")
# team_dict = {}
# result = []
# for j in range(N):
#     for i in range(M):
#         if value[i, j] == 1:
#             if i not in team_dict:
#                 team_dict[i] = len(team_dict) + 1
#             result.append(str(team_dict[i]))
#             break
# print(" -> ".join(result))

for j in range(N):
    for i in range(M):
        if value[i, j] == 1:
            if i not in team_dict:
                team_dict[i] = len(team_dict) + 1
            result.append(str(team_dict[i]))
            break
print(" -> ".join(result))

if __name__ == '__main__':
    pass