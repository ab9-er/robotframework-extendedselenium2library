#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 Richard Huang <rickypc@users.noreply.github.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import Selenium2Library
import sys
#from ExtendedSelenium2Library.locators import ExtendedElementFinder
from ExtendedSelenium2Library.version import get_version
from robot import utils
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of, visibility_of
from time import sleep, time

__version__ = get_version()


class ExtendedSelenium2Library(Selenium2Library.Selenium2Library):
    """ExtendedSelenium2Library is a web testing library with AngularJS support and
    custom improvement for Robot Framework.

    It uses the Selenium 2 (WebDriver) libraries internally to control a web browser.
    See http://seleniumhq.org/docs/03_webdriver.html for more information on Selenium 2
    and WebDriver.

    ExtendedSelenium2Library runs tests in a real browser instance. It should work in
    most modern browsers and can be used with both Python and Jython interpreters.

    = Before running tests =

    Prior to running test cases using ExtendedSelenium2Library, ExtendedSelenium2Library must be
    imported into your Robot test suite (see `importing` section), and the
    `Open Browser` keyword must be used to open a browser to the desired location.

    = Locating elements =

    All keywords in ExtendedSelenium2Library that need to find an element on the page
    take an argument, `locator`. By default, when a locator value is provided,
    it is matched against the key attributes of the particular element type.
    For example, `id` and `name` are key attributes to all elements, and
    locating elements is easy using just the `id` as a `locator`. For example::

    Click Element  my_element

    It is also possible to specify the approach ExtendedSelenium2Library should take
    to find an element by specifying a lookup strategy with a locator
    prefix. Supported strategies are:

    | *Strategy*   | *Example*                                       | *Description*                                      |
    | identifier   | Click Element `|` identifier=my_element         | Matches by @id or @name attribute                  |
    | id           | Click Element `|` id=my_element                 | Matches by @id attribute                           |
    | name         | Click Element `|` name=my_element               | Matches by @name attribute                         |
    | xpath        | Click Element `|` xpath=//div[@id='my_element'] | Matches with arbitrary XPath expression            |
    | dom          | Click Element `|` dom=document.images[56]       | Matches with arbitrary DOM express                 |
    | link         | Click Element `|` link=My Link                  | Matches anchor elements by their link text         |
    | partial link | Click Element `|` partial link=y Lin            | Matches anchor elements by their partial link text |
    | css          | Click Element `|` css=div.my_class              | Matches by CSS selector                            |
    | jquery       | Click Element `|` jquery=div.my_class           | Matches by jQuery/sizzle selector                  |
    | sizzle       | Click Element `|` sizzle=div.my_class           | Matches by jQuery/sizzle selector                  |
    | tag          | Click Element `|` tag=div                       | Matches by HTML tag name                           |
    | default*     | Click Link    `|` default=page?a=b              | Matches key attributes with value after first '='  |

    * Explicitly specifying the default strategy is only necessary if locating
    elements by matching key attributes is desired and an attribute value
    contains a '='. The following would fail because it appears as if _page?a_
    is the specified lookup strategy:
    | Click Link    page?a=b
    This can be fixed by changing the locator to:
    | Click Link    default=page?a=b

    Table related keywords, such as `Table Should Contain`, work differently.
    By default, when a table locator value is provided, it will search for
    a table with the specified `id` attribute. For example:

    Table Should Contain  my_table  text

    More complex table lookup strategies are also supported:

    | *Strategy* | *Example*                                                          | *Description*                     |
    | css        | Table Should Contain `|` css=table.my_class `|` text               | Matches by @id or @name attribute |
    | xpath      | Table Should Contain `|` xpath=//table/[@name="my_table"] `|` text | Matches by @id or @name attribute |

    = Timeouts =

    There are several `Wait ...` keywords that take timeout as an
    argument. All of these timeout arguments are optional. The timeout
    used by all of them can be set globally using the
    `Set Selenium Timeout` keyword. The same timeout also applies to
    `Execute Async Javascript`.

    All timeouts can be given as numbers considered seconds (e.g. 0.5 or 42)
    or in Robot Framework's time syntax (e.g. '1.5 seconds' or '1 min 30 s').
    For more information about the time syntax see:
    http://robotframework.googlecode.com/svn/trunk/doc/userguide/RobotFrameworkUserGuide.html#time-format.
    """

    NG_WRAPPER = '%(prefix)s' \
                 'angular.element(document.querySelector(\'[data-ng-app]\')||document).injector().' \
                 'get(\'$browser\').notifyWhenNoOutstandingRequests(%(handler)s)' \
                 '%(suffix)s'
    ROBOT_EXIT_ON_FAILURE = True
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, timeout=90.0, implicit_wait=15.0, run_on_failure='Capture Page Screenshot',
                 block_until_page_ready=True, browser_breath_delay=0.05, poll_frequency=0.2):
        """ExtendedSelenium2Library can be imported with optional arguments.

        `timeout` is the default timeout used to wait for all waiting actions.
        It can be later set with `Set Selenium Timeout`.

        'implicit_wait' is the implicit timeout that Selenium waits when
        looking for elements.
        It can be later set with `Set Selenium Implicit Wait`.
        See `WebDriver: Advanced Usage`__ section of the SeleniumHQ documentation
        for more information about WebDriver's implicit wait functionality.

        __ http://seleniumhq.org/docs/04_webdriver_advanced.html#explicit-and-implicit-waits

        `run_on_failure` specifies the name of a keyword (from any available
        libraries) to execute when a ExtendedSelenium2Library keyword fails. By default
        `Capture Page Screenshot` will be used to take a screenshot of the current page.
        Using the value "Nothing" will disable this feature altogether. See
        `Register Keyword To Run On Failure` keyword for more information about this
        functionality.

        Examples:
        | Library `|` ExtendedSelenium2Library `|` 15                                            | # Sets default timeout to 15 seconds                                       |
        | Library `|` ExtendedSelenium2Library `|` 0 `|` 5                                       | # Sets default timeout to 0 seconds and default implicit_wait to 5 seconds |
        | Library `|` ExtendedSelenium2Library `|` 5 `|` run_on_failure=Log Source               | # Sets default timeout to 5 seconds and runs `Log Source` on failure       |
        | Library `|` ExtendedSelenium2Library `|` implicit_wait=5 `|` run_on_failure=Log Source | # Sets default implicit_wait to 5 seconds and runs `Log Source` on failure |
        | Library `|` ExtendedSelenium2Library `|` timeout=10      `|` run_on_failure=Nothing    | # Sets default timeout to 10 seconds and does nothing on failure           |
        """
        Selenium2Library.Selenium2Library.__init__(self, timeout, implicit_wait, run_on_failure)
        self._block_until_page_ready = block_until_page_ready
        self._browser_breath_delay = 0.05 if browser_breath_delay is None else float(browser_breath_delay)
        self._poll_frequency = 0.2 if poll_frequency is None else float(poll_frequency)
        #self._element_finder = ExtendedElementFinder()

    def click_button(self, locator):
        """Clicks a button identified by `locator`.

        Key attributes for buttons are `id`, `name` and `value`. See
        `introduction` for details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).click_button(locator)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def click_element(self, locator):
        """Click element identified by `locator`.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).click_element(locator)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def click_element_at_coordinates(self, locator, xoffset, yoffset):
        """Click element identified by `locator` at x/y coordinates of the element.
        Cursor is moved and the center of the element and x/y coordinates are
        calculted from that point.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).click_element_at_coordinates(locator, xoffset, yoffset)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def click_image(self, locator):
        """Clicks an image found by `locator`.

        Key attributes for images are `id`, `src` and `alt`. See
        `introduction` for details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).click_image(locator)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def click_link(self, locator):
        """Clicks a link identified by locator.

        Key attributes for links are `id`, `name`, `href` and link text. See
        `introduction` for details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).click_link(locator)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def double_click_element(self, locator):
        """Double click element identified by `locator`.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).double_click_element(locator)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def is_element_visible(self, locator):
        """Returns element visibility identified by `locator`.

        Key attributes for arbitrary elements are `id` and `name`. See
        `introduction` for details about locating elements.
        """
        return self._is_visible(locator)

    def location_should_be(self, url):
        """Verifies that current URL is exactly `url`."""
        # cross browser support
        actual = self._current_browser().execute_script('return document.location.href')
        if  actual != url:
            raise AssertionError("Location should have been '%s' but was '%s'." % (url, actual))
        self._debug("Current location is '%s'." % url)

    def open_browser(self, url, browser='firefox', alias=None,remote_url=False,
                     desired_capabilities=None,ff_profile_dir=None):
        """Opens a new browser instance to given URL.

        Returns the index of this browser instance which can be used later to
        switch back to it. Index starts from 1 and is reset back to it when
        `Close All Browsers` keyword is used. See `Switch Browser` for
        example.

        Optional alias is an alias for the browser instance and it can be used
        for switching between browsers (just as index can be used). See `Switch
        Browser` for more details.

        Possible values for `browser` are as follows:

        | firefox          | FireFox                         |
        | ff               | FireFox                         |
        | internetexplorer | Internet Explorer               |
        | ie               | Internet Explorer               |
        | googlechrome     | Google Chrome                   |
        | gc               | Google Chrome                   |
        | chrome           | Google Chrome                   |
        | opera            | Opera                           |
        | phantomjs        | PhantomJS                       |
        | htmlunit         | HTMLUnit                        |
        | htmlunitwithjs   | HTMLUnit with Javascipt support |
        | android          | Android                         |
        | iphone           | Iphone                          |
        | safari           | Safari                          |

        Note, that you will encounter strange behavior, if you open
        multiple Internet Explorer browser instances. That is also why
        `Switch Browser` only works with one IE browser at most.
        For more information see:
        http://selenium-grid.seleniumhq.org/faq.html#i_get_some_strange_errors_when_i_run_multiple_internet_explorer_instances_on_the_same_machine

        Optional 'remote_url' is the url for a remote selenium server for example
        http://127.0.0.1/wd/hub.  If you specify a value for remote you can
        also specify 'desired_capabilities' which is a string in the form
        key1:val1,key2:val2 that will be used to specify desired_capabilities
        to the remote server. This is useful for doing things like specify a
        proxy server for internet explorer or for specify browser and os if your
        using saucelabs.com. 'desired_capabilities' can also be a dictonary
        (created with 'Create Dictionary') to allow for more complex configurations.

        Optional 'ff_profile_dir' is the path to the firefox profile dir if you
        wish to overwrite the default.
        """
        index = super(ExtendedSelenium2Library, self).open_browser(url, browser, alias, remote_url,
                                                                   desired_capabilities, ff_profile_dir)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()
        return index

    def select_all_from_list(self, locator):
        """Selects all values from multi-select list identified by `id`.

        Key attributes for lists are `id` and `name`. See `introduction` for
        details about locating elements.
        """
        super(ExtendedSelenium2Library, self).select_all_from_list(locator)
        self._element_trigger_change(locator)

    def select_checkbox(self, locator):
        """Selects checkbox identified by `locator`.

        Does nothing if checkbox is already selected. Key attributes for
        checkboxes are `id` and `name`. See `introduction` for details about
        locating elements.
        """
        self._info("Selecting checkbox '%s'." % locator)
        element = self._get_checkbox(locator)
        if not element.is_selected():
            self._select_checkbox_or_radio_button(element)

    def select_from_list(self, locator, *items):
        """Selects `*items` from list identified by `locator`

        If more than one value is given for a single-selection list, the last
        value will be selected. If the target list is a multi-selection list,
        and `*items` is an empty list, all values of the list will be selected.

        *items try to select by value then by label.

        It's faster to use 'by index/value/label' functions.

        An exception is raised for a single-selection list if the last
        value does not exist in the list and a warning for all other non-
        existing items. For a multi-selection list, an exception is raised
        for any and all non-existing values.

        Select list keywords work on both lists and combo boxes. Key attributes for
        select lists are `id` and `name`. See `introduction` for details about
        locating elements.
        """
        super(ExtendedSelenium2Library, self).select_from_list(locator, *items)
        self._element_trigger_change(locator)

    def select_from_list_by_index(self, locator, *indexes):
        """Selects `*indexes` from list identified by `locator`

        Select list keywords work on both lists and combo boxes. Key attributes for
        select lists are `id` and `name`. See `introduction` for details about
        locating elements.
        """
        super(ExtendedSelenium2Library, self).select_from_list_by_index(locator, *indexes)
        self._element_trigger_change(locator)

    def select_from_list_by_label(self, locator, *labels):
        """Selects `*labels` from list identified by `locator`

        Select list keywords work on both lists and combo boxes. Key attributes for
        select lists are `id` and `name`. See `introduction` for details about
        locating elements.
        """
        super(ExtendedSelenium2Library, self).select_from_list_by_label(locator, *labels)
        self._element_trigger_change(locator)

    def select_from_list_by_value(self, locator, *values):
        """Selects `*values` from list identified by `locator`

        Select list keywords work on both lists and combo boxes. Key attributes for
        select lists are `id` and `name`. See `introduction` for details about
        locating elements.
        """
        super(ExtendedSelenium2Library, self).select_from_list_by_value(locator, *values)
        self._element_trigger_change(locator)

    def select_radio_button(self, group_name, value):
        """Sets selection of radio button group identified by `group_name` to `value`.

        The radio button to be selected is located by two arguments:
        - `group_name` is used as the name of the radio input
        - `value` is used for the value attribute or for the id attribute

        The XPath used to locate the correct radio button then looks like this:
        //input[@type='radio' and @name='group_name' and (@value='value' or @id='value')]

        Examples:
        | Select Radio Button | size | XL | # Matches HTML like <input type="radio" name="size" value="XL">XL</input> |
        | Select Radio Button | size | sizeXL | # Matches HTML like <input type="radio" name="size" value="XL" id="sizeXL">XL</input> |
        """
        self._info("Selecting '%s' from radio button '%s'." % (value, group_name))
        element = self._get_radio_button_with_value(group_name, value)
        if not element.is_selected():
            self._select_checkbox_or_radio_button(element)

    def submit_form(self, locator):
        """Submits a form identified by `locator`.

        If `locator` is empty, first form in the page will be submitted.
        Key attributes for forms are `id` and `name`. See `introduction` for
        details about locating elements.
        """
        self._scroll_into_view(locator)
        super(ExtendedSelenium2Library, self).submit_form(locator)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def wait_for_async_condition(self, condition, timeout=None, error=None):
        """Waits until the given asynchronous `condition` is true or `timeout` expires.

        The `condition` can be arbitrary JavaScript expression but must explicitly signal they are finished
        by invoking the provided callback at the end.
        See `Execute Async Javascript` for information about executing asynchronous JavaScript.

        `error` can be used to override the default error message.

        See `introduction` for more information about `timeout` and its default value.

        See also `Wait For Condition`, `Wait Until Page Contains`, `Wait Until Page Contains
        Element`, `Wait Until Element Is Visible` and BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        timeout = self._timeout_in_secs if timeout is None else utils.timestr_to_secs(timeout)
        if not error:
            error = "Condition '%s' did not become true in %s" % (condition, self._format_timeout(timeout))
        WebDriverWait(self._current_browser(), timeout, self._poll_frequency).\
            until(lambda driver: driver.execute_async_script(js), error)

    def wait_until_angular_ready(self, timeout=None, error=None):
        """Waits until AngularJS is ready to process next request or `timeout` expires.

        `error` can be used to override the default error message.

        See `introduction` for more information about `timeout` and its
        default value.

        See also `Wait For Condition`, `Wait Until Page Contains`,
        `Wait Until Page Contains Element`, `Wait Until Element Is Visible`
        and BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        timeout = self._implicit_wait_in_secs if timeout is None else utils.timestr_to_secs(timeout)
        if not error:
            error = 'AngularJS is not ready in %s' % self._format_timeout(timeout)
        # we add more validation here to support transition between AngularJs to non AngularJS page.
        js = self.NG_WRAPPER % {'prefix': 'var cb=arguments[arguments.length-1];if(window.angular){',
                                'handler': 'function(){cb(true)}',
                                'suffix': '}else{cb(true)}'}
        try:
            WebDriverWait(self._current_browser(), timeout, self._poll_frequency).\
                until(lambda driver: driver.execute_async_script(js), error)
        except:
            self._debug(sys.exc_info()[0])
            # still inflight, second chance. let the browser take a deep breath...
            sleep(self._browser_breath_delay)
            try:
                WebDriverWait(self._current_browser(), timeout, self._poll_frequency).\
                    until(lambda driver: driver.execute_async_script(js), error)
            except:
                # instead of halting the process because AngularJS is not ready in <TIMEOUT>, we try our luck...
                self._debug(sys.exc_info()[0])
                pass

    def wait_until_element_is_not_visible(self, locator, timeout=None, error=None):
        """Waits until element specified with `locator` is not visible.

        Fails if `timeout` expires before the element is not visible. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Element Is Visible`, `Wait Until Page Contains`,
        `Wait Until Page Contains Element`, `Wait For Condition` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        timeout = self._implicit_wait_in_secs if timeout is None else utils.timestr_to_secs(timeout)
        if not error:
            error = 'Element \'%s\' was still visible after %s' % (locator, self._format_timeout(timeout))
        element = self._element_find(locator, True, True)
        if element is None:
            raise AssertionError("Element '%s' not found." % locator)
        WebDriverWait(None, timeout, self._poll_frequency).until_not(visibility_of(element), error)

    def wait_until_element_is_visible(self, locator, timeout=None, error=None):
        """Waits until element specified with `locator` is visible.

        Fails if `timeout` expires before the element is visible. See
        `introduction` for more information about `timeout` and its
        default value.

        `error` can be used to override the default error message.

        See also `Wait Until Element Is Not Visible`, `Wait Until Page Contains`,
        `Wait Until Page Contains Element`, `Wait For Condition` and
        BuiltIn keyword `Wait Until Keyword Succeeds`.
        """
        timeout = self._implicit_wait_in_secs if timeout is None else utils.timestr_to_secs(timeout)
        if not error:
            error = 'Element \'%s\' was not visible in %s' % (locator, self._format_timeout(timeout))
        element = self._element_find(locator, True, True)
        if element is None:
            raise AssertionError("Element '%s' not found." % locator)
        WebDriverWait(None, timeout, self._poll_frequency).until(visibility_of(element), error)

    def _angular_select_checkbox_or_radio_button(self, element):
        if element is None:
            raise AssertionError("Element not found.")
        # you will operating in different scope
        js = self.NG_WRAPPER % {'prefix': 'var obj=arguments[0];',
                                'handler': 'function(){angular.element(obj).prop(\'checked\',true).'
                                'triggerHandler(\'click\')}',
                                'suffix': ''}
        self._debug("Executing JavaScript:\n%s" % js)
        self._current_browser().execute_script(js, element)
        self._wait_until_page_ready()
        self.wait_until_angular_ready()

    def _element_trigger_change(self, locator):
        element = self._element_find(locator, True, True)
        if element is None:
            raise AssertionError("Element '%s' not found." % locator)
        if self._is_angular_control(element):
            # you will operating in different scope
            js = self.NG_WRAPPER % {'prefix': 'var obj=arguments[0];',
                                    'handler': 'function(){angular.element(obj).triggerHandler(\'change\')}',
                                    'suffix': ''}
            self._debug("Executing JavaScript:\n%s" % js)
            self._current_browser().execute_script(js, element)
            self._wait_until_page_ready()
            self.wait_until_angular_ready()
        else:
            self._wait_until_page_ready()

    def _get_browser_name(self):
        return self._current_browser().capabilities['browserName'].strip().lower()

    def _input_text_into_text_field(self, locator, text):
        element = self._element_find(locator, True, True)
        if self._is_angular_control(element):
            # you will operating in different scope
            js = self.NG_WRAPPER % {'prefix': 'var obj=arguments[0];var text=arguments[1];',
                                    'handler': 'function(){var el=angular.element(obj).val(text);' +
                                               'el.triggerHandler(\'change\');el.triggerHandler(\'blur\')}',
                                    'suffix': ''}
            self._debug("Executing JavaScript:\n%s" % js)
            self._current_browser().execute_script(js, element, text)
            self._wait_until_page_ready()
            self.wait_until_angular_ready()
        else:
            # *** run these into separate contexts to reduce race condition ***
            browser_name = self._get_browser_name()
            event = '' if self._is_firefox(browser_name) else 'event'
            # focus window first, before focus to the requested field
            js = ("try{window.focus();$(arguments[0]).trigger('focus',[%(event)s])}" +
                 "catch(x){arguments[0].focus(%(event)s)}") % {'event': event}
            self._debug("Executing JavaScript:\n%s" % js)
            self._current_browser().execute_script(js, element)
            if self._is_internet_explorer(browser_name):
                # let the browser take a deep breath...
                sleep(self._browser_breath_delay)
            js = ("try{$(arguments[0]).val(arguments[1]).trigger('keyup',[%(event)s])}" +
                 "catch(x){arguments[0].value=arguments[1]}") % {'event': event}
            self._debug("Executing JavaScript:\n%s" % js)
            self._current_browser().execute_script(js, element, text)
            if self._is_internet_explorer(browser_name):
                # let the browser take a deep breath...
                sleep(self._browser_breath_delay)
            # blur the window, will blur the field :)
            js = "try{window.blur()}catch(x){arguments[0].onblur()}"
            self._debug("Executing JavaScript:\n%s" % js)
            self._current_browser().execute_script(js, element)

    def _is_angular_control(self, element):
        if self._is_angular_page():
            self._debug('Validating Angular control: %s' % element.get_attribute('outerHTML'))
            return element.get_attribute('data-ng-model') != '' or element.get_attribute('ng-model') != ''
        else:
            return False

    def _is_angular_page(self):
        js = 'return !!window.angular'
        self._debug("Executing JavaScript: %s" % js)
        try:
            return self._current_browser().execute_script(js)
        except:
            self._debug(sys.exc_info()[0])
            return False

    def _is_firefox(self, browser_name=None):
        if not browser_name:
            browser_name = self._get_browser_name()
        return browser_name == 'firefox' or browser_name == 'ff'

    def _is_internet_explorer(self, browser_name=None):
        if not browser_name:
            browser_name = self._get_browser_name()
        return browser_name == 'internetexplorer' or browser_name == 'ie'

    def _scroll_into_view(self, locator):
        if self._is_internet_explorer():
            element = self._element_find(locator, True, True)
            if element is None:
                raise AssertionError("Element '%s' not found." % locator)
            js = 'arguments[0].scrollIntoView(true)'
            self._debug("Executing JavaScript:\n%s" % js)
            self._current_browser().execute_script(js, element)

    def _select_checkbox_or_radio_button(self, element):
        if self._is_angular_control(element):
            self._angular_select_checkbox_or_radio_button(element)
        else:
            element.click()
            self._wait_until_page_ready()

    # semi blocking API that incorporated different strategies for cross browser support
    def _wait_until_page_ready(self, timeout=None):
        if self._block_until_page_ready:
            delay = self._browser_breath_delay
            if delay < 1:
                delay *= 10
            # let the browser take a deep breath...
            sleep(delay)
            timeout = self._implicit_wait_in_secs if timeout is None else utils.timestr_to_secs(timeout)
            browser = self._current_browser()
            js = 'return (document.readyState===\'complete\' && !!document.body && !!document.body.childNodes.length)'
            try:
                WebDriverWait(None, timeout, self._poll_frequency).\
                    until_not(staleness_of(browser.find_element_by_tag_name('body')), '')
            except:
                # instead of halting the process because document is not ready in <TIMEOUT>, we try our luck...
                self._debug(sys.exc_info()[0])
                pass
            try:
                WebDriverWait(browser, timeout, self._poll_frequency).\
                    until(lambda driver: driver.execute_script(js), '')
            except:
                # instead of halting the process because document is not ready in <TIMEOUT>, we try our luck...
                self._debug(sys.exc_info()[0])
                pass