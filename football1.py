"""This file contains code for use with "Think Bayes",
by Allen B. Downey, available from greenteapress.com

Copyright 2014 Allen B. Downey
License: GNU GPLv3 http://www.gnu.org/licenses/gpl.html
"""

from __future__ import print_function, division

import numpy
import thinkbayes2
import thinkplot
from scrape import scrape_team

class Football():
    """ Represents hypotheses about a Football teams offense,
    in terms of TDs per game and FGs per games
    """

    def __init__(self, hypos):
        self.TD = ScoreType(hypos[0])
        self.FG = ScoreType(hypos[1])

    def Update(self, data):
        """Update the child PMFs based on the data.
        data = (time since last TD, time since last FG)
        """
        self.score.Update(data[0])
        self.TD.Update(data[0])
        self.FG.Update(data[1])

    def UpdateFG(self, delta_time):
        """Update the child PMF based on the data.
        delta_time = time since last FG
        """
        self.FG.Update(delta_time)

    def UpdateTD(self, delta_time):
        """Update the child PMF based on the data.
        delta_time = time since last TD
        """
        self.TD.Update(delta_time)

    def PredRemaining(self, rem_time, points_scored):
        """Plots the predictive distribution for final number of goals.

        rem_time: remaining time in the game in minutes
        points_scored: points already scored
        """
        FGpredict = self.FG.PredRemaining(rem_time, 0)
        TDpredict = self.TD.PredRemaining(rem_time, 0)
        GoalTotal = FGpredict * 3 + TDpredict * 7
        GoalTotal += points_scored
        return GoalTotal

class ScoreType(thinkbayes2.Suite):
    """Represents hypotheses about the lambda parameter of a
    Poisson Process to generate scores.
    """

    def Likelihood(self, data, hypo):
        """Computes the likelihood of the data under the hypothesis.

        hypo: hypothetical goal scoring rate in goals per game
        data: time between goals in minutes
        """
        x = data #time between goals in minutes
        lam = hypo/60.0 #goals per minute
        like = thinkbayes2.EvalExponentialPdf(x,lam) #evaluating for every value of lamda
        return like

    def PredRemaining(self, rem_time, score):
        """Plots the predictive distribution for final number of goals.

        rem_time: remaining time in the game in minutes
        score: number of goals already scored
        """
        metapmf=thinkbayes2.Pmf() #PMF about PMFS. probabilities of pmf values
        for lam, prob in self.Items(): #loop through probabilities of lamdas
            #print(lam,prob)
            lt = lam*rem_time/60
            pmf=thinkbayes2.MakePoissonPmf(lt,20)
            #thinkplot.Pdf(pmf,linewidth=1,alpha=0.2,color='purple')
            metapmf[pmf]=prob

        mix = thinkbayes2.MakeMixture(metapmf)
        mix += score #shift by 2 because we've already seen 2
        return mix

def constructPriors():
    """Constructs an even prior for both teams, and then
    uses data from www.covers.com from the 2014 season to
    update the priors
    """

    eagles_url = "/pageLoader/pageLoader.aspx?page=/data/nfl/teams/pastresults/2014-2015/team7.html"
    giants_url = "/pageLoader/pageLoader.aspx?page=/data/nfl/teams/pastresults/2014-2015/team8.html"

    eagles = Football((numpy.linspace(0, 20, 201), numpy.linspace(0, 20, 201)))
    giants = Football((numpy.linspace(0, 20, 201), numpy.linspace(0, 20, 201)))

    eagles_data = scrape_team(eagles_url)
    giants_data = scrape_team(giants_url)

    last_time_FG_eagles = 0
    last_time_TD_eagles = 0
    for game in eagles_data:
        last_time_FG_eagles += 60.0
        last_time_TD_eagles += 60.0
        for item in game:
            if item[2] == "Eagles":
                if item[1] == "FG":
                    rem_time = item[0]
                    inter_arrival = last_time_FG_eagles - rem_time
                    last_time_FG_eagles = rem_time

                    eagles.UpdateFG(inter_arrival)
                if item[1] == "TD":
                    rem_time = item[0]
                    inter_arrival = last_time_TD_eagles - rem_time
                    last_time_TD_eagles = rem_time

                    eagles.UpdateTD(inter_arrival)

    last_time_FG_giants = 0
    last_time_TD_giants = 0
    for game in giants_data:
        last_time_FG_giants += 60.0
        last_time_TD_giants += 60.0
        for item in game:
            if item[2] == "Giants":
                if item[1] == "FG":
                    rem_time = item[0]
                    inter_arrival = last_time_FG_giants - rem_time
                    last_time_FG_giants = rem_time

                    giants.UpdateFG(inter_arrival)
                if item[1] == "TD":
                    rem_time = item[0]
                    inter_arrival = last_time_TD_giants - rem_time
                    last_time_TD_giants = rem_time

                    giants.UpdateTD(inter_arrival)

    return eagles, giants


def main():
    """Look at the October 12th, 2014 game between the Giants and the Eagles,
    and predict the probabilities of each team winning.
    """

    eagles, giants = constructPriors()

    GoalTotalGiants = giants.PredRemaining(60, 0)
    GoalTotalEagles = eagles.PredRemaining(60, 0)
    print("Giants win", GoalTotalEagles.ProbLess(GoalTotal_giants))
    print("Eagles win", GoalTotalGiants.ProbLess(GoalTotal_eagles))
    print(GoalTotalEagles.MakeCdf().CredibleInterval(90))
    print(GoalTotalGiants.MakeCdf().CredibleInterval(90))

if __name__ == '__main__':
    main()
